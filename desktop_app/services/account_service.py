"""Account & Group management service."""
from __future__ import annotations

import base64
import contextlib
import datetime as _dt
import json
import os
import re
import select
import shutil
import socket
import socketserver
import ssl
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

from typing import Any, Callable, Sequence

import httpx

from desktop_app.database import DATA_DIR
from desktop_app.database.models import Account, Asset, Device, Group, Task
from desktop_app.database.repository import Repository
from desktop_app.services.activity_service import ActivityService


_BROWSER_HEADERS = {
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/134.0.0.0 Safari/537.36"
    ),
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
}

_PLATFORM_AUTH_COOKIES = {
    "tiktok": {"sessionid", "sessionid_ss", "sid_tt", "uid_tt"},
    "tiktok_shop": {"sessionid", "sessionid_ss", "sid_tt", "uid_tt"},
    "instagram": {"sessionid", "ds_user_id", "csrftoken"},
}

_PLATFORM_HOME_URLS = {
    "tiktok": "https://www.tiktok.com/",
    "tiktok_shop": "https://seller.tiktokglobalshop.com/",
    "instagram": "https://www.instagram.com/",
}

_PLATFORM_DEFAULT_COOKIE_DOMAINS = {
    "tiktok": ".tiktok.com",
    "tiktok_shop": ".tiktokglobalshop.com",
    "instagram": ".instagram.com",
}

_ACCOUNT_SESSION_EXTENSION_NAME = "TKOPS Account Session"


@dataclass(slots=True)
class _ProxyEndpoint:
    raw: str
    scheme: str
    username: str | None
    password: str | None
    host: str
    port: int

    @property
    def host_port(self) -> str:
        return f"{self.host}:{self.port}"

    @property
    def display(self) -> str:
        if self.username:
            return f"{self.scheme}://{self.username}:***@{self.host}:{self.port}"
        return f"{self.scheme}://{self.host}:{self.port}"

    @property
    def upstream_url(self) -> str:
        if self.username is None:
            return f"{self.scheme}://{self.host}:{self.port}"
        username = quote(self.username, safe="")
        password = quote(self.password or "", safe="")
        return f"{self.scheme}://{username}:{password}@{self.host}:{self.port}"

    @property
    def auth_present(self) -> bool:
        return self.username is not None


class AccountEnvironmentError(ValueError):
    def __init__(self, message: str, *, code: str) -> None:
        super().__init__(message)
        self.code = code


class _ProxyRelayServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(
        self,
        server_address: tuple[str, int],
        request_handler_class,
        relay: "_ProxyRelay",
    ) -> None:
        super().__init__(server_address, request_handler_class)
        self.relay = relay


class _ProxyRelayHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        self.server.relay.handle_client(self.connection)  # type: ignore[attr-defined]


class _ProxyRelay:
    def __init__(self, endpoint: _ProxyEndpoint, timeout: float = 8.0) -> None:
        self._endpoint = endpoint
        self._timeout = timeout
        self._server = _ProxyRelayServer(("127.0.0.1", 0), _ProxyRelayHandler, self)
        self._thread = threading.Thread(
            target=self._server.serve_forever,
            name="tkops-proxy-relay",
            daemon=True,
        )
        self._thread.start()

    def _open_upstream(self) -> socket.socket:
        upstream = socket.create_connection((self._endpoint.host, self._endpoint.port), timeout=self._timeout)
        upstream.settimeout(self._timeout)
        if self._endpoint.scheme == "https":
            context = ssl.create_default_context()
            upstream = context.wrap_socket(upstream, server_hostname=self._endpoint.host)
            upstream.settimeout(self._timeout)
        return upstream

    @property
    def local_endpoint(self) -> str:
        host, port = self._server.server_address
        return f"{host}:{port}"

    def close(self) -> None:
        with contextlib.suppress(Exception):
            self._server.shutdown()
        with contextlib.suppress(Exception):
            self._server.server_close()
        if self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def handle_client(self, client_socket: socket.socket) -> None:
        try:
            request_line, headers, body = self._read_request(client_socket)
            if not request_line:
                return
            method, _target, _version = request_line.split(" ", 2)
            upstream = self._open_upstream()
            try:
                if method.upper() == "CONNECT":
                    self._handle_connect(client_socket, upstream, request_line, headers)
                else:
                    upstream.sendall(self._build_forwarded_request(request_line, headers, body))
                    self._relay_response(client_socket, upstream)
            finally:
                with contextlib.suppress(Exception):
                    upstream.close()
        except Exception:
            with contextlib.suppress(Exception):
                client_socket.sendall(
                    b"HTTP/1.1 502 Bad Gateway\r\n"
                    b"Content-Length: 0\r\n"
                    b"Connection: close\r\n\r\n"
                )

    def _read_request(self, client_socket: socket.socket) -> tuple[str, list[str], bytes]:
        data = b""
        while b"\r\n\r\n" not in data:
            chunk = client_socket.recv(4096)
            if not chunk:
                break
            data += chunk
            if len(data) > 131072:
                raise ValueError("request too large")
        if b"\r\n\r\n" not in data:
            return "", [], b""

        head, body = data.split(b"\r\n\r\n", 1)
        lines = head.split(b"\r\n")
        request_line = lines[0].decode("iso-8859-1")
        headers = [line.decode("iso-8859-1") for line in lines[1:] if line]

        content_length = 0
        for header in headers:
            name, _, value = header.partition(":")
            if name.lower().strip() == "content-length":
                with contextlib.suppress(ValueError):
                    content_length = int(value.strip())

        while len(body) < content_length:
            chunk = client_socket.recv(4096)
            if not chunk:
                break
            body += chunk

        return request_line, headers, body[:content_length]

    def _inject_proxy_auth(self, header_lines: list[str]) -> list[str]:
        auth = self._proxy_authorization_header()
        filtered = [line for line in header_lines if not line.lower().startswith("proxy-authorization:")]
        if auth:
            filtered.insert(0, f"Proxy-Authorization: {auth}")
        return filtered

    def _proxy_authorization_header(self) -> str | None:
        if not self._endpoint.auth_present:
            return None
        token = base64.b64encode(
            f"{self._endpoint.username}:{self._endpoint.password or ''}".encode("utf-8")
        ).decode("ascii")
        return f"Basic {token}"

    def _build_forwarded_request(self, request_line: str, headers: list[str], body: bytes) -> bytes:
        filtered_headers: list[str] = []
        saw_connection = False
        for header in self._inject_proxy_auth(headers):
            name, _, _value = header.partition(":")
            lower = name.lower().strip()
            if lower == "proxy-connection":
                continue
            if lower == "connection":
                saw_connection = True
                filtered_headers.append("Connection: close")
                continue
            filtered_headers.append(header)
        if not saw_connection:
            filtered_headers.append("Connection: close")
        payload = request_line + "\r\n" + "\r\n".join(filtered_headers) + "\r\n\r\n"
        return payload.encode("iso-8859-1") + body

    def _handle_connect(
        self,
        client_socket: socket.socket,
        upstream: socket.socket,
        request_line: str,
        headers: list[str],
    ) -> None:
        upstream.sendall(self._build_forwarded_request(request_line, headers, b""))
        response_head = self._read_response_head(upstream)
        client_socket.sendall(response_head)
        status_line = response_head.split(b"\r\n", 1)[0].decode("iso-8859-1", errors="ignore")
        if " 200 " not in status_line:
            return
        self._relay_bidirectional(client_socket, upstream)

    def _read_response_head(self, upstream: socket.socket) -> bytes:
        data = b""
        while b"\r\n\r\n" not in data:
            chunk = upstream.recv(4096)
            if not chunk:
                break
            data += chunk
            if len(data) > 131072:
                raise ValueError("response too large")
        if b"\r\n\r\n" not in data:
            return data
        return data.split(b"\r\n\r\n", 1)[0] + b"\r\n\r\n"

    def _relay_response(self, client_socket: socket.socket, upstream: socket.socket) -> None:
        while True:
            data = upstream.recv(8192)
            if not data:
                break
            client_socket.sendall(data)

    def _relay_bidirectional(self, client_socket: socket.socket, upstream: socket.socket) -> None:
        sockets = [client_socket, upstream]
        while sockets:
            readable, _, exceptional = select.select(sockets, [], sockets, self._timeout)
            if exceptional:
                break
            if not readable:
                continue
            for sock in readable:
                try:
                    data = sock.recv(8192)
                except OSError:
                    data = b""
                if not data:
                    return
                other = upstream if sock is client_socket else client_socket
                other.sendall(data)


class _LauncherProbeHttpServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(
        self,
        server_address: tuple[str, int],
        request_handler_class,
        probe_callback: Callable[[], dict[str, Any]],
    ) -> None:
        super().__init__(server_address, request_handler_class)
        self.probe_callback = probe_callback


class _LauncherProbeHandler(BaseHTTPRequestHandler):
    server: _LauncherProbeHttpServer

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        if self.path.split("?", 1)[0] != "/status":
            self.send_error(404)
            return
        try:
            payload_obj = self.server.probe_callback()
        except Exception as exc:
            payload_obj = {
                "ok": False,
                "message": f"代理检测服务异常：{exc}",
                "status_code": None,
                "egress_ip": "",
                "detail": str(exc),
                "target_ok": False,
                "target_status_code": None,
                "checked_at": _dt.datetime.now().isoformat(timespec="seconds"),
            }
        payload = json.dumps(payload_obj, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def _send_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")


class _LauncherProbe:
    def __init__(self, probe_callback: Callable[[], dict[str, Any]]) -> None:
        self._server = _LauncherProbeHttpServer(("127.0.0.1", 0), _LauncherProbeHandler, probe_callback)
        self._thread = threading.Thread(
            target=self._server.serve_forever,
            name="tkops-launcher-probe",
            daemon=True,
        )
        self._thread.start()

    @property
    def status_url(self) -> str:
        host, port = self._server.server_address[:2]
        return f"http://{host}:{port}/status"

    def close(self) -> None:
        with contextlib.suppress(Exception):
            self._server.shutdown()
        with contextlib.suppress(Exception):
            self._server.server_close()


class _AccountSessionStatusHttpServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(
        self,
        server_address: tuple[str, int],
        request_handler_class,
        tracker: "_AccountSessionTracker",
    ) -> None:
        super().__init__(server_address, request_handler_class)
        self.tracker = tracker


class _AccountSessionStatusHandler(BaseHTTPRequestHandler):
    server: _AccountSessionStatusHttpServer

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        if self.path.split("?", 1)[0] != "/status":
            self.send_error(404)
            return
        payload = json.dumps(self.server.tracker.snapshot(), ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self) -> None:  # noqa: N802
        if self.path.split("?", 1)[0] != "/report":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length > 0 else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8"))
        except Exception:
            payload = {}
        self.server.tracker.update(payload if isinstance(payload, dict) else {})
        response = b'{"ok":true}'
        self.send_response(200)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def _send_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")


class _AccountSessionTracker:
    def __init__(self, account_id: int) -> None:
        self._lock = threading.Lock()
        self._state: dict[str, Any] = {
            "accountId": int(account_id),
            "status": "pending",
            "loginStatus": "pending",
            "appliedCount": 0,
            "failed": [],
            "message": "正在等待系统自动加载的登录扩展注入账号 Cookie，无需手动安装插件",
            "updatedAt": _dt.datetime.now().isoformat(timespec="seconds"),
        }
        self._server = _AccountSessionStatusHttpServer(("127.0.0.1", 0), _AccountSessionStatusHandler, self)
        self._thread = threading.Thread(
            target=self._server.serve_forever,
            name=f"tkops-account-session-{account_id}",
            daemon=True,
        )
        self._thread.start()

    @property
    def status_url(self) -> str:
        host, port = self._server.server_address
        return f"http://{host}:{port}/status"

    @property
    def report_url(self) -> str:
        host, port = self._server.server_address
        return f"http://{host}:{port}/report"

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return dict(self._state)

    def update(self, payload: dict[str, Any]) -> None:
        with self._lock:
            self._state.update(payload)
            self._state["updatedAt"] = _dt.datetime.now().isoformat(timespec="seconds")

    def close(self) -> None:
        with contextlib.suppress(Exception):
            self._server.shutdown()
        with contextlib.suppress(Exception):
            self._server.server_close()
        if self._thread.is_alive():
            self._thread.join(timeout=1.0)


class AccountService:
    def __init__(self, repo: Repository | None = None) -> None:
        self._repo = repo or Repository()
        self._device_proxy_relays: dict[int, _ProxyRelay] = {}
        self._launcher_probes: dict[int, _LauncherProbe] = {}
        self._account_session_trackers: dict[int, _AccountSessionTracker] = {}

    def create_account(self, username: str, **kwargs: Any) -> Account:
        payload = self._normalize_account_fields(kwargs)
        payload.setdefault("risk_status", "normal")
        account = self._repo.add(Account(username=username, **payload))
        self._log_account_activity(
            "account_created",
            "创建账号",
            account.id,
            {
                "message": f"账号 {account.username} 已创建",
                "manual_status": account.status,
                "risk_status": account.risk_status,
            },
        )
        return account

    def list_accounts(
        self,
        *,
        status: str | None = None,
        query: str | None = None,
        manual_status: str | None = None,
        system_status: str | None = None,
        risk_status: str | None = None,
        include_archived: bool = False,
    ) -> Sequence[Account]:
        accounts = list(
            self._repo.list_accounts(
                status=status,
                manual_status=manual_status,
                query=query,
                risk_status=risk_status,
                include_archived=include_archived,
            )
        )
        if system_status:
            accounts = [
                account for account in accounts if self._resolve_system_status(account) == system_status
            ]
        return accounts

    def get_account(self, pk: int) -> Account | None:
        return self._repo.get_by_id(Account, pk)

    def update_account(self, pk: int, **fields: Any) -> Account | None:
        account = self._repo.get_by_id(Account, pk)
        if account is None:
            return None
        payload = self._normalize_account_fields(fields)
        updated = self._repo.update(account, **payload)
        self._log_account_activity(
            "account_updated",
            "更新账号",
            updated.id,
            {
                "message": f"账号 {updated.username} 已更新",
                "manual_status": updated.status,
                "risk_status": getattr(updated, "risk_status", "normal"),
            },
        )
        return updated

    def get_account_detail(self, pk: int, *, activity_limit: int = 5) -> dict[str, Any] | None:
        account = self.get_account(pk)
        if account is None:
            return None
        return {
            "account": account,
            "activitySummary": self.list_account_activity_summary(pk, limit=activity_limit),
            "systemStatus": self._resolve_system_status(account),
            "lastError": self._resolve_last_error(account),
        }

    def list_account_activity_summary(self, account_id: int, *, limit: int = 5) -> list[dict[str, Any]]:
        rows = self._repo.list_activity_logs(
            related_entity_type="account",
            related_entity_id=int(account_id),
        )[:limit]
        summary: list[dict[str, Any]] = []
        for row in rows:
            payload = ActivityService._load_payload(row.payload_json)
            summary.append(
                {
                    "title": row.title,
                    "summary": str(payload.get("message") or payload.get("summary") or "").strip(),
                    "occurredAt": row.created_at.isoformat() if row.created_at else None,
                }
            )
        return summary

    def bulk_update_accounts(
        self,
        account_ids: Sequence[int],
        *,
        action: str,
        manual_status: str | None = None,
        risk_status: str | None = None,
        group_id: int | None = None,
        archive_reason: str | None = None,
    ) -> dict[str, Any]:
        processed_ids: list[int] = []
        for account_id in [int(item) for item in account_ids if int(item)]:
            if action in {"set_manual_status", "manual_status"}:
                updated = self.update_account(account_id, status=manual_status or "active")
                if updated is not None:
                    processed_ids.append(updated.id)
            elif action in {"set_risk_status", "risk_status"}:
                updated = self.update_account(account_id, risk_status=risk_status or "normal")
                if updated is not None:
                    processed_ids.append(updated.id)
            elif action in {"assign_group", "group"}:
                updated = self.update_account(account_id, group_id=group_id)
                if updated is not None:
                    processed_ids.append(updated.id)
            elif action == "archive":
                archived = self.archive_account(account_id, reason=archive_reason)
                if archived is not None:
                    processed_ids.append(account_id)
            elif action == "unarchive":
                restored = self.unarchive_account(account_id)
                if restored is not None:
                    processed_ids.append(account_id)
            elif action in {"test_connection", "test"}:
                self.test_account_connection(account_id)
                processed_ids.append(account_id)
            else:
                raise ValueError("不支持的批量动作")
        return {
            "action": action,
            "processed": len(processed_ids),
            "accountIds": processed_ids,
            "manualStatus": manual_status,
            "riskStatus": risk_status,
            "groupId": group_id,
            "archiveReason": archive_reason,
        }

    def archive_account(self, pk: int, *, reason: str | None = None) -> dict[str, Any] | None:
        account = self._repo.get_by_id(Account, pk)
        if account is None:
            return None
        archived = self._repo.update(
            account,
            archived_at=_dt.datetime.now(),
            archived_reason=(reason or "").strip() or None,
        )
        self._log_account_activity(
            "account_archived",
            "归档账号",
            archived.id,
            {"message": f"账号 {archived.username} 已归档", "reason": archived.archived_reason},
        )
        return {"accountId": archived.id, "archived": True, "archiveReason": archived.archived_reason}

    def unarchive_account(self, pk: int) -> dict[str, Any] | None:
        account = self._repo.get_by_id(Account, pk)
        if account is None:
            return None
        restored = self._repo.update(account, archived_at=None, archived_reason=None)
        self._log_account_activity(
            "account_unarchived",
            "取消归档",
            restored.id,
            {"message": f"账号 {restored.username} 已取消归档"},
        )
        return {"accountId": restored.id, "archived": False}

    def delete_account(self, pk: int) -> bool:
        account = self._repo.get_by_id(Account, pk)
        if account is None:
            return False
        session = self._repo.session
        try:
            session.query(Task).filter(Task.account_id == pk).update(
                {Task.account_id: None}, synchronize_session="fetch"
            )
            session.query(Asset).filter(Asset.account_id == pk).update(
                {Asset.account_id: None}, synchronize_session="fetch"
            )
            self._log_account_activity(
                "account_deleted",
                "删除账号",
                account.id,
                {"message": f"账号 {account.username} 已删除"},
            )
            session.delete(account)
            session.commit()
            session.expire_all()
        except Exception:
            session.rollback()
            raise
        return True

    def bind_device(self, account_id: int, device_id: int) -> Account | None:
        return self.update_account(account_id, device_id=device_id)

    def test_account_connection(self, pk: int, *, timeout: float = 2.5) -> dict[str, Any]:
        account = self._repo.get_by_id(Account, pk)
        if account is None:
            raise ValueError("账号不存在")

        device = account.device
        target_host, target_port = self._resolve_account_target(device)
        checked_at = _dt.datetime.now()
        ok = False
        latency_ms: int | None = None
        message = ""

        if target_host:
            started = _dt.datetime.now()
            try:
                connection = socket.create_connection((target_host, target_port), timeout=timeout)
                connection.close()
                latency_ms = max(
                    1,
                    int((_dt.datetime.now() - started).total_seconds() * 1000),
                )
                ok = True
                message = "连接成功"
            except OSError as exc:
                detail = exc.strerror or str(exc) or "网络不可达"
                message = f"连接失败：{detail}"
        else:
            message = "当前账号未绑定可检测的代理地址"

        updated = self.update_account(
            pk,
            last_connection_status="reachable" if ok else "unreachable",
            last_connection_checked_at=checked_at,
            last_connection_message=message,
        )
        if updated is None:
            raise ValueError("账号不存在")

        self._log_account_activity(
            "account_connection_tested",
            "账号连接检测",
            updated.id,
            {
                "message": message,
                "system_status": "reachable" if ok else "unreachable",
                "checked_at": checked_at.isoformat(),
                "latency_ms": latency_ms,
            },
        )

        return {
            "account_id": updated.id,
            "username": updated.username,
            "ok": ok,
            "target": f"{target_host}:{target_port}" if target_host else "",
            "latency_ms": latency_ms,
            "checked_at": checked_at,
            "message": message,
            "scope": "proxy_tcp_reachability",
            "scope_label": "仅检测代理可达性，不校验平台登录态",
            "cookie_status": updated.cookie_status,
            "isolation_enabled": updated.isolation_enabled,
            "device_status": device.status if device else "unknown",
            "proxy_status": device.proxy_status if device else "unknown",
        }

    def _normalize_account_fields(self, fields: dict[str, Any]) -> dict[str, Any]:
        payload = dict(fields)
        normalized: dict[str, Any] = {}
        field_map = {
            "username": "username",
            "platform": "platform",
            "region": "region",
            "status": "status",
            "followers": "followers",
            "group_id": "group_id",
            "device_id": "device_id",
            "cookie_status": "cookie_status",
            "cookie_content": "cookie_content",
            "cookie_updated_at": "cookie_updated_at",
            "isolation_enabled": "isolation_enabled",
            "last_connection_status": "last_connection_status",
            "last_connection_message": "last_connection_message",
            "last_connection_checked_at": "last_connection_checked_at",
            "last_login_check_status": "last_login_check_status",
            "last_login_check_at": "last_login_check_at",
            "last_login_check_message": "last_login_check_message",
            "last_login_at": "last_login_at",
            "notes": "notes",
            "tags": "tags",
            "risk_status": "risk_status",
            "archived_at": "archived_at",
            "archived_reason": "archived_reason",
        }
        for key, target in field_map.items():
            if key in payload:
                normalized[target] = payload[key]
        return normalized

    def _resolve_system_status(self, account: Account) -> str:
        login_status = str(account.last_login_check_status or "unknown")
        if login_status != "unknown":
            return login_status
        return str(account.last_connection_status or "unknown")

    def _resolve_last_error(self, account: Account) -> str | None:
        return (
            account.last_login_check_message
            or account.last_connection_message
            or None
        )

    def _log_account_activity(
        self,
        category: str,
        title: str,
        account_id: int,
        payload: dict[str, Any],
    ) -> None:
        ActivityService(self._repo).create_activity_log(
            category,
            title,
            payload_json=json.dumps(payload, ensure_ascii=False),
            related_entity_type="account",
            related_entity_id=int(account_id),
        )

    def validate_account_login(self, pk: int, *, timeout: float = 10.0) -> dict[str, Any]:
        account = self._repo.get_by_id(Account, pk)
        if account is None:
            raise ValueError("账号不存在")

        raw_cookie = str(account.cookie_content or "").strip()
        if not raw_cookie:
            raise ValueError("请先导入或粘贴 Cookie 内容，再执行登录态校验")

        cookie_entries = self._parse_cookie_entries(raw_cookie)
        if not cookie_entries:
            raise ValueError("当前 Cookie 内容无法解析，请导入浏览器导出的完整 Cookie 文件")

        checked_at = _dt.datetime.now()
        proxy_url = self._build_proxy_url(account.device.proxy_ip if account.device else None)
        result = self._run_login_validation(account, cookie_entries, proxy_url=proxy_url, timeout=timeout)

        update_fields: dict[str, Any] = {
            "last_login_check_status": result["status"],
            "last_login_check_at": checked_at,
            "last_login_check_message": result["message"],
        }
        if result["status"] in {"valid", "proxy_mismatch"}:
            update_fields["cookie_status"] = "valid"
            update_fields["last_login_at"] = checked_at
        elif result["status"] == "invalid":
            update_fields["cookie_status"] = "invalid"

        updated = self.update_account(pk, **update_fields)
        if updated is None:
            raise ValueError("账号不存在")

        return {
            "account_id": updated.id,
            "username": updated.username,
            "status": result["status"],
            "label": result["label"],
            "message": result["message"],
            "checked_at": checked_at,
            "platform": updated.platform,
            "target": result.get("target", ""),
            "http_status": result.get("http_status"),
            "via_proxy": bool(proxy_url),
            "cookie_status": updated.cookie_status,
        }

    def _resolve_account_target(self, device: Device | None) -> tuple[str | None, int]:
        if device is None or not device.proxy_ip:
            return None, 443

        raw = str(device.proxy_ip).strip()
        if not raw:
            return None, 443
        if "://" in raw:
            raw = raw.split("://", 1)[1]
        raw = raw.split("/", 1)[0]
        if "@" in raw:
            raw = raw.rsplit("@", 1)[-1]

        host = raw
        port = 443
        if raw.count(":") == 1:
            maybe_host, maybe_port = raw.rsplit(":", 1)
            if maybe_port.isdigit():
                host = maybe_host.strip()
                port = int(maybe_port)

        return (host or None), port

    def _parse_proxy_endpoint(self, raw_proxy: str) -> _ProxyEndpoint:
        raw = str(raw_proxy or "").strip()
        if not raw:
            raise ValueError("代理地址不能为空")
        if "://" not in raw:
            raw = "http://" + raw

        parsed = urlsplit(raw)
        scheme = str(parsed.scheme or "").lower()
        if scheme not in {"http", "https"}:
            raise ValueError("仅支持 http:// 或 https:// 开头的代理地址")

        host = str(parsed.hostname or "").strip()
        port = parsed.port
        if not host or port is None:
            raise ValueError("代理地址必须包含 host:port")

        username = unquote(parsed.username) if parsed.username is not None else None
        password = unquote(parsed.password) if parsed.password is not None else None
        if username == "":
            username = None

        return _ProxyEndpoint(
            raw=raw,
            scheme=scheme,
            username=username,
            password=password,
            host=host,
            port=int(port),
        )

    def _validate_proxy_endpoint(
        self,
        endpoint: _ProxyEndpoint,
        *,
        timeout: float = 8.0,
    ) -> dict[str, Any]:
        try:
            with httpx.Client(
                timeout=timeout,
                follow_redirects=True,
                headers=dict(_BROWSER_HEADERS),
                proxy=endpoint.upstream_url,
            ) as client:
                response = client.get("https://api.ipify.org?format=json")
                payload = (
                    response.json()
                    if response.headers.get("content-type", "").startswith("application/json")
                    else {}
                )
                ip = payload.get("ip") if isinstance(payload, dict) else ""
                if response.status_code == 200 and ip:
                    return {
                        "ok": True,
                        "message": "代理连通性验证通过",
                        "status_code": response.status_code,
                        "egress_ip": str(ip),
                        "detail": f"出口 IP {ip}",
                    }
                return {
                    "ok": False,
                    "message": f"代理验证失败：HTTP {response.status_code}",
                    "status_code": response.status_code,
                    "egress_ip": "",
                    "detail": f"HTTP {response.status_code}",
                }
        except (httpx.TimeoutException, httpx.ProxyError, httpx.NetworkError, httpx.HTTPError, ValueError) as exc:
            detail = str(exc) or type(exc).__name__
            return {
                "ok": False,
                "message": f"代理验证失败：{detail}",
                "status_code": None,
                "egress_ip": "",
                "detail": detail,
            }

    def _release_device_proxy_relay(self, device_id: int) -> None:
        relay = self._device_proxy_relays.pop(int(device_id), None)
        if relay is not None:
            relay.close()

    def _release_launcher_probe(self, device_id: int) -> None:
        probe = self._launcher_probes.pop(int(device_id), None)
        if probe is not None:
            probe.close()

    def _start_device_proxy_relay(self, device_id: int, endpoint: _ProxyEndpoint) -> _ProxyRelay:
        self._release_device_proxy_relay(device_id)
        relay = _ProxyRelay(endpoint)
        self._device_proxy_relays[int(device_id)] = relay
        return relay

    def _start_launcher_probe(self, device_id: int, *, proxy_url: str, target_url: str) -> _LauncherProbe:
        self._release_launcher_probe(device_id)
        probe = _LauncherProbe(
            lambda: self._probe_browser_proxy(proxy_url=proxy_url, target_url=target_url)
        )
        self._launcher_probes[int(device_id)] = probe
        return probe

    def _probe_browser_proxy(
        self,
        *,
        proxy_url: str,
        target_url: str,
        timeout: float = 8.0,
    ) -> dict[str, Any]:
        checked_at = _dt.datetime.now().isoformat(timespec="seconds")
        try:
            with httpx.Client(
                timeout=timeout,
                follow_redirects=True,
                headers=dict(_BROWSER_HEADERS),
                proxy=proxy_url,
            ) as client:
                ip_response = client.get("https://api.ipify.org?format=json")
                payload = (
                    ip_response.json()
                    if ip_response.headers.get("content-type", "").startswith("application/json")
                    else {}
                )
                ip = payload.get("ip") if isinstance(payload, dict) else ""
                if ip_response.status_code != 200 or not ip:
                    return {
                        "ok": False,
                        "message": f"出口 IP 探测失败：HTTP {ip_response.status_code}",
                        "status_code": ip_response.status_code,
                        "egress_ip": "",
                        "detail": f"HTTP {ip_response.status_code}",
                        "target_ok": False,
                        "target_status_code": None,
                        "checked_at": checked_at,
                    }
                target_ok: bool | None = None
                target_status_code: int | None = None
                target_detail = f"出口 IP {ip}"
                if str(target_url or "").strip():
                    try:
                        target_response = client.get(target_url)
                        target_status_code = int(target_response.status_code)
                        target_ok = 200 <= target_response.status_code < 400
                        if target_ok:
                            target_detail = f"出口 IP {ip}，TikTok 探测 HTTP {target_response.status_code}"
                        else:
                            target_detail = f"出口 IP {ip}，TikTok 探测 HTTP {target_response.status_code}"
                    except (httpx.TimeoutException, httpx.ProxyError, httpx.NetworkError, httpx.HTTPError, ValueError) as exc:
                        target_ok = False
                        target_status_code = None
                        target_detail = f"出口 IP {ip}，TikTok 探测失败：{str(exc) or type(exc).__name__}"
                return {
                    "ok": True,
                    "message": "代理连通性验证通过",
                    "status_code": ip_response.status_code,
                    "egress_ip": str(ip),
                    "detail": target_detail,
                    "target_ok": target_ok,
                    "target_status_code": target_status_code,
                    "checked_at": checked_at,
                }
        except (httpx.TimeoutException, httpx.ProxyError, httpx.NetworkError, httpx.HTTPError, ValueError) as exc:
            detail = str(exc) or type(exc).__name__
            return {
                "ok": False,
                "message": f"代理验证失败：{detail}",
                "status_code": None,
                "egress_ip": "",
                "detail": detail,
                "target_ok": False,
                "target_status_code": None,
                "checked_at": checked_at,
            }

    def _run_login_validation(
        self,
        account: Account,
        cookie_entries: list[dict[str, Any]],
        *,
        proxy_url: str | None,
        timeout: float,
    ) -> dict[str, Any]:
        platform = str(account.platform or "").strip().lower()
        if platform in {"tiktok", "tiktok_shop"}:
            validator = self._validate_tiktok_login
        elif platform == "instagram":
            validator = self._validate_instagram_login
        else:
            return {
                "status": "unknown",
                "label": "暂不支持",
                "message": f"当前平台 {account.platform or '未知'} 暂不支持自动登录态校验",
                "target": "",
                "http_status": None,
            }

        cookie_names = {str(item.get("name", "")).strip().lower() for item in cookie_entries if item.get("name")}
        required = _PLATFORM_AUTH_COOKIES.get(platform, set())
        if required and not (cookie_names & required):
            return {
                "status": "invalid",
                "label": "校验失败",
                "message": "导入的 Cookie 缺少核心登录字段，当前无法证明账号处于已登录状态",
                "target": "",
                "http_status": None,
            }

        cookies = self._build_cookie_jar(cookie_entries)

        if proxy_url:
            proxied_result = self._execute_login_validation_attempt(
                account,
                validator,
                cookies,
                proxy_url=proxy_url,
                timeout=timeout,
            )
            if proxied_result["status"] == "valid":
                proxied_result["message"] += "（通过绑定代理校验）"
                return proxied_result

            direct_result = self._execute_login_validation_attempt(
                account,
                validator,
                cookies,
                proxy_url=None,
                timeout=timeout,
            )
            if direct_result["status"] == "valid":
                return {
                    "status": "proxy_mismatch",
                    "label": "代理冲突",
                    "message": (
                        "Cookie 直连校验通过，但通过绑定代理校验失败。"
                        + (proxied_result.get("message") or "代理侧返回了异常结果")
                    ),
                    "target": proxied_result.get("target") or direct_result.get("target") or "",
                    "http_status": proxied_result.get("http_status"),
                }
            if proxied_result["status"] == "invalid":
                return proxied_result
            if direct_result["status"] == "invalid":
                return direct_result
            proxied_message = proxied_result.get("message") or ""
            direct_message = direct_result.get("message") or ""
            if proxied_message and direct_message and proxied_message != direct_message:
                proxied_result["message"] = proxied_message + "；直连复核：" + direct_message
            return proxied_result

        return self._execute_login_validation_attempt(
            account,
            validator,
            cookies,
            proxy_url=None,
            timeout=timeout,
        )

    def _execute_login_validation_attempt(
        self,
        account: Account,
        validator,
        cookies: httpx.Cookies,
        *,
        proxy_url: str | None,
        timeout: float,
    ) -> dict[str, Any]:
        client_kwargs: dict[str, Any] = {
            "timeout": timeout,
            "follow_redirects": True,
            "headers": dict(_BROWSER_HEADERS),
            "cookies": cookies,
        }
        if proxy_url:
            client_kwargs["proxy"] = proxy_url

        try:
            with httpx.Client(**client_kwargs) as client:
                return validator(client, account)
        except (httpx.TimeoutException, httpx.ProxyError, httpx.NetworkError, httpx.HTTPError) as exc:
            detail = self._normalize_http_error(exc)
            return {
                "status": "unknown",
                "label": "校验未完成",
                "message": f"登录态校验未完成：{detail}",
                "target": "",
                "http_status": None,
            }

    def _validate_tiktok_login(self, client: httpx.Client, account: Account) -> dict[str, Any]:
        endpoints = [
            (
                "https://www.tiktok.com/passport/web/account/info/",
                {
                    "aid": "1459",
                    "app_language": "zh-Hans",
                    "language": "zh-Hans",
                    "region": str(account.region or "US").upper(),
                },
            ),
            (
                "https://www.tiktok.com/api/me/",
                {
                    "aid": "1988",
                    "app_language": "zh-Hans",
                    "language": "zh-Hans",
                    "region": str(account.region or "US").upper(),
                },
            ),
        ]
        reasons: list[str] = []
        for url, params in endpoints:
            response = client.get(
                url,
                params=params,
                headers={
                    "accept": "application/json, text/plain, */*",
                    "referer": "https://www.tiktok.com/",
                    "x-requested-with": "XMLHttpRequest",
                },
            )
            payload = self._safe_json(response)
            if response.status_code in {401, 403} or self._payload_indicates_invalid_login(payload):
                detail = self._extract_error_message(payload) or f"HTTP {response.status_code}"
                return {
                    "status": "invalid",
                    "label": "未登录",
                    "message": f"TikTok 返回未登录或已失效：{detail}",
                    "target": str(response.request.url),
                    "http_status": response.status_code,
                }
            identity = self._extract_tiktok_identity(payload)
            if identity:
                return {
                    "status": "valid",
                    "label": "已登录",
                    "message": f"已通过 TikTok 账号接口确认登录态，可识别账号 {identity}",
                    "target": str(response.request.url),
                    "http_status": response.status_code,
                }
            reasons.append(f"{response.status_code}/{response.headers.get('content-type', 'unknown')}")

        html_result = self._validate_tiktok_html_identity(client)
        if html_result:
            return html_result

        return {
            "status": "unknown",
            "label": "无法确认",
            "message": "TikTok 已响应，但没有返回明确的账号信息，可能被风控页面或挑战页拦截：" + "；".join(reasons),
            "target": endpoints[0][0],
            "http_status": None,
        }

    def _validate_tiktok_html_identity(self, client: httpx.Client) -> dict[str, Any] | None:
        response = client.get(
            "https://www.tiktok.com/",
            headers={
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "referer": "https://www.tiktok.com/",
            },
        )
        if response.status_code in {401, 403}:
            return {
                "status": "invalid",
                "label": "未登录",
                "message": f"TikTok 根页返回未登录状态：HTTP {response.status_code}",
                "target": str(response.request.url),
                "http_status": response.status_code,
            }

        identity = self._extract_tiktok_identity_from_html(response.text)
        if response.status_code == 200 and identity:
            return {
                "status": "valid",
                "label": "已登录",
                "message": f"已通过 TikTok 页面态确认登录，可识别账号 {identity}",
                "target": str(response.request.url),
                "http_status": response.status_code,
            }
        return None

    def _validate_instagram_login(self, client: httpx.Client, account: Account) -> dict[str, Any]:
        response = client.get(
            "https://www.instagram.com/api/v1/accounts/current_user/?edit=true",
            headers={
                "accept": "application/json, text/plain, */*",
                "referer": "https://www.instagram.com/",
                "x-ig-app-id": "936619743392459",
                "x-requested-with": "XMLHttpRequest",
            },
        )
        payload = self._safe_json(response)
        user = payload.get("user") if isinstance(payload, dict) else None
        username = ""
        if isinstance(user, dict):
            username = str(user.get("username") or "").strip()
        if response.status_code == 200 and username:
            return {
                "status": "valid",
                "label": "已登录",
                "message": f"已通过 Instagram 当前用户接口确认登录态，可识别账号 {username}",
                "target": str(response.request.url),
                "http_status": response.status_code,
            }
        if response.status_code in {401, 403} or self._payload_indicates_invalid_login(payload):
            detail = self._extract_error_message(payload) or f"HTTP {response.status_code}"
            return {
                "status": "invalid",
                "label": "未登录",
                "message": f"Instagram 返回未登录或已失效：{detail}",
                "target": str(response.request.url),
                "http_status": response.status_code,
            }
        return {
            "status": "unknown",
            "label": "无法确认",
            "message": "Instagram 已响应，但没有返回明确的当前用户信息，可能需要重新登录或补齐浏览器导出的完整 Cookie",
            "target": str(response.request.url),
            "http_status": response.status_code,
        }

    def infer_cookie_status(self, raw_value: str) -> dict[str, str]:
        facts = self._extract_cookie_facts(raw_value)
        now_ms = int(_dt.datetime.now().timestamp() * 1000)
        within_48h_ms = 48 * 60 * 60 * 1000
        if facts["count"] == 0:
            return {"status": "missing", "label": "缺失"}
        if facts["has_expiry"] and facts["valid_count"] == 0 and facts["expired_count"] > 0:
            return {"status": "invalid", "label": "已失效"}
        nearest_expiry_ms = facts["nearest_expiry_ms"]
        if nearest_expiry_ms is not None and nearest_expiry_ms <= now_ms:
            return {"status": "invalid", "label": "已失效"}
        if nearest_expiry_ms is not None and (nearest_expiry_ms - now_ms) <= within_48h_ms:
            return {"status": "expiring", "label": "48 小时内过期"}
        return {"status": "valid", "label": "有效"}

    def _extract_cookie_facts(self, raw_value: str) -> dict[str, Any]:
        facts = {
            "count": 0,
            "valid_count": 0,
            "expired_count": 0,
            "nearest_expiry_ms": None,
            "has_expiry": False,
        }
        for cookie in self._parse_cookie_entries(raw_value):
            expires_at = self._resolve_cookie_expiry(cookie)
            facts["count"] += 1
            if expires_at is None:
                facts["valid_count"] += 1
                continue
            facts["has_expiry"] = True
            if facts["nearest_expiry_ms"] is None or expires_at < facts["nearest_expiry_ms"]:
                facts["nearest_expiry_ms"] = expires_at
            if expires_at <= int(_dt.datetime.now().timestamp() * 1000):
                facts["expired_count"] += 1
            else:
                facts["valid_count"] += 1
        return facts

    def _build_proxy_url(self, raw_proxy: str | None) -> str | None:
        if not raw_proxy:
            return None
        value = str(raw_proxy).strip()
        if not value:
            return None
        if "://" in value:
            return value
        return f"http://{value}"

    def _build_cookie_jar(self, cookie_entries: list[dict[str, Any]]) -> httpx.Cookies:
        jar = httpx.Cookies()
        for item in cookie_entries:
            name = str(item.get("name") or "").strip()
            if not name:
                continue
            value = str(item.get("value") or "")
            domain = str(item.get("domain") or "").strip() or None
            path = str(item.get("path") or "/").strip() or "/"
            if domain:
                jar.set(name, value, domain=domain, path=path)
            else:
                jar.set(name, value, path=path)
        return jar

    def _parse_cookie_entries(self, raw_value: str) -> list[dict[str, Any]]:
        raw = str(raw_value or "").strip()
        if not raw:
            return []
        entries = self._parse_cookie_json(raw)
        if not entries:
            entries = self._parse_cookie_netscape(raw)
        if not entries:
            entries = self._parse_cookie_string(raw)
        return [item for item in entries if str(item.get("name") or "").strip()]

    def _parse_cookie_json(self, raw: str) -> list[dict[str, Any]]:
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return []
        if isinstance(parsed, list):
            return [item for item in parsed if isinstance(item, dict)]
        if isinstance(parsed, dict) and isinstance(parsed.get("cookies"), list):
            return [item for item in parsed["cookies"] if isinstance(item, dict)]
        return []

    def _parse_cookie_netscape(self, raw: str) -> list[dict[str, Any]]:
        cookies: list[dict[str, Any]] = []
        for line in raw.splitlines():
            entry = line.strip()
            if not entry or entry.startswith("#"):
                continue
            parts = entry.split("\t")
            if len(parts) < 7:
                continue
            cookies.append({
                "domain": parts[0],
                "path": parts[2],
                "expires": parts[4],
                "name": parts[5],
                "value": parts[6],
            })
        return cookies

    def _parse_cookie_string(self, raw: str) -> list[dict[str, Any]]:
        cookies: list[dict[str, Any]] = []
        for part in raw.split(";"):
            item = part.strip()
            if not item or "=" not in item:
                continue
            name, value = item.split("=", 1)
            cookies.append({"name": name.strip(), "value": value.strip()})
        return cookies

    def _resolve_cookie_expiry(self, cookie: dict[str, Any]) -> int | None:
        for key in ("expirationDate", "expires", "expiry", "expiration", "expiresAt"):
            value = cookie.get(key)
            if value in (None, ""):
                continue
            try:
                numeric = float(value)
            except (TypeError, ValueError):
                numeric = None
            if numeric is not None:
                if numeric < 100000000000:
                    return int(numeric * 1000)
                return int(numeric)
            try:
                return int(_dt.datetime.fromisoformat(str(value).replace("Z", "+00:00")).timestamp() * 1000)
            except ValueError:
                continue
        return None

    def _safe_json(self, response: httpx.Response) -> dict[str, Any]:
        try:
            payload = response.json()
        except ValueError:
            return {}
        return payload if isinstance(payload, dict) else {}

    def _extract_tiktok_identity(self, payload: dict[str, Any]) -> str:
        identity_keys = (
            "username",
            "user_name",
            "userName",
            "unique_id",
            "uniqueId",
            "screen_name",
            "screenName",
            "nickname",
            "nick_name",
            "display_name",
            "displayName",
            "user_id",
            "userId",
            "user_id_str",
            "uid",
            "uid_str",
        )
        queue: list[Any] = [payload]
        seen: set[int] = set()
        while queue:
            candidate = queue.pop(0)
            if not isinstance(candidate, dict):
                continue
            marker = id(candidate)
            if marker in seen:
                continue
            seen.add(marker)
            for key in identity_keys:
                value = candidate.get(key)
                if value not in (None, ""):
                    return str(value).strip()
            for nested in candidate.values():
                if isinstance(nested, dict):
                    queue.append(nested)
        return ""

    def _extract_tiktok_identity_from_html(self, html: str) -> str:
        text = str(html or "")
        patterns = [
            r'"username"\s*:\s*"([^"]{3,80})"',
            r'"uniqueId"\s*:\s*"([^"]{3,80})"',
            r'"screen_name"\s*:\s*"([^"]{3,80})"',
            r'"user_id"\s*:\s*"?([0-9]{6,30})"?',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return ""

    def _payload_indicates_invalid_login(self, payload: dict[str, Any]) -> bool:
        for message in self._iter_payload_error_texts(payload):
            lowered = message.lower()
            invalid_markers = (
                "not login",
                "not logged",
                "login_required",
                "login expired",
                "session expired",
                "unauthorized",
                "challenge_required",
                "checkpoint_required",
                "captcha",
                "verify",
                "verification",
                "please login",
                "please log in",
                "请登录",
                "未登录",
                "登录已过期",
                "挑战",
                "验证码",
                "验证",
                "风控",
            )
            if any(marker in lowered for marker in invalid_markers):
                return True
        return False

    def _extract_error_message(self, payload: dict[str, Any]) -> str:
        for text in self._iter_payload_error_texts(payload):
            if text:
                return text
        return ""

    def _iter_payload_error_texts(self, payload: Any):
        for mapping in self._iter_payload_mappings(payload):
            for key in ("message", "status_msg", "error_message", "description", "detail"):
                value = mapping.get(key)
                if value:
                    yield str(value)

    def _iter_payload_mappings(self, payload: Any):
        if isinstance(payload, dict):
            yield payload
            for value in payload.values():
                yield from self._iter_payload_mappings(value)
        elif isinstance(payload, list):
            for item in payload:
                yield from self._iter_payload_mappings(item)

    def _normalize_http_error(self, exc: Exception) -> str:
        detail = getattr(exc, "message", None) or str(exc) or type(exc).__name__
        return detail.replace("[Errno 11001]", "网络解析失败")

    # ── Groups ──

    def create_group(self, name: str, **kwargs: Any) -> Group:
        return self._repo.add(Group(name=name, **kwargs))

    def list_groups(self) -> Sequence[Group]:
        return self._repo.list_groups()

    def update_group(self, pk: int, **fields: Any) -> Group | None:
        group = self._repo.get_by_id(Group, pk)
        if group is None:
            return None
        return self._repo.update(group, **fields)

    def delete_group(self, pk: int) -> bool:
        group = self._repo.get_by_id(Group, pk)
        if group is None:
            return False
        self._repo.delete(group)
        return True

    def assign_group(self, account_id: int, group_id: int) -> Account | None:
        return self.update_account(account_id, group_id=group_id)

    # ── Devices ──

    def list_devices(self, *, status: str | None = None) -> Sequence[Device]:
        return self._repo.list_devices(status=status)

    def create_device(self, device_code: str, name: str, **kwargs: Any) -> Device:
        normalized = self._normalize_device_runtime_fields(kwargs)
        return self._repo.add(Device(device_code=device_code, name=name, **normalized))

    def get_device(self, pk: int) -> Device | None:
        return self._repo.get_by_id(Device, pk)

    def update_device(self, pk: int, **fields: Any) -> Device | None:
        device = self._repo.get_by_id(Device, pk)
        if device is None:
            return None
        normalized = self._normalize_device_runtime_fields(fields, existing=device)
        return self._repo.update(device, **normalized)

    def delete_device(self, pk: int) -> bool:
        device = self._repo.get_by_id(Device, pk)
        if device is None:
            return False
        self._release_device_proxy_relay(pk)
        self._release_launcher_probe(pk)
        self._repo.delete(device)
        return True

    def inspect_device(self, pk: int, *, timeout: float = 2.0) -> dict[str, Any]:
        device = self._repo.get_by_id(Device, pk)
        if device is None:
            raise ValueError("设备不存在")

        bound_accounts = list(device.accounts or [])
        target_host, target_port = self._resolve_account_target(device)
        checked_at = _dt.datetime.now()
        ok = False
        latency_ms: int | None = None
        message = ""

        if target_host:
            started = _dt.datetime.now()
            try:
                connection = socket.create_connection((target_host, target_port), timeout=timeout)
                connection.close()
                latency_ms = max(1, int((_dt.datetime.now() - started).total_seconds() * 1000))
                ok = True
                message = "代理连通成功"
            except OSError as exc:
                detail = exc.strerror or str(exc) or "网络不可达"
                message = f"代理连通失败：{detail}"
        else:
            message = "当前设备未配置可检测的代理地址"

        proxy_status = self._derive_inspected_proxy_status(target_host, ok)
        status = self._derive_inspected_device_status(device, bound_accounts, proxy_status)
        updated = self.update_device(pk, proxy_status=proxy_status, status=status)
        if updated is None:
            raise ValueError("设备不存在")

        return {
            "device_id": updated.id,
            "device_code": updated.device_code,
            "name": updated.name,
            "ok": ok,
            "target": f"{target_host}:{target_port}" if target_host else "",
            "latency_ms": latency_ms,
            "checked_at": checked_at,
            "message": message,
            "scope": "proxy_tcp_reachability",
            "scope_label": "检测设备代理可达性，并结合指纹与账号绑定状态回写设备状态",
            "status": updated.status,
            "proxy_status": updated.proxy_status,
            "fingerprint_status": updated.fingerprint_status,
            "bound_accounts": len(bound_accounts),
        }

    def repair_device_environment(self, pk: int) -> dict[str, Any]:
        inspection = self.inspect_device(pk)
        device = self._repo.get_by_id(Device, pk)
        if device is None:
            raise ValueError("设备不存在")

        profile_dir = self._ensure_device_profile(device)
        actions = ["已同步设备状态", "已准备浏览器独立 Profile"]

        if inspection["proxy_status"] != "online":
            actions.append("代理链路仍异常，需要人工修复代理或网络")
        if str(device.fingerprint_status or "").lower() == "missing":
            actions.append("指纹缺失，仍需人工补齐")
        elif str(device.fingerprint_status or "").lower() == "drifted":
            actions.append("指纹漂移，建议人工重建")

        return {
            "device_id": device.id,
            "device_code": device.device_code,
            "status": device.status,
            "proxy_status": device.proxy_status,
            "profile_dir": str(profile_dir),
            "actions": actions,
            "inspection": inspection,
        }

    def open_account_environment(self, pk: int) -> dict[str, Any]:
        account = self._repo.get_by_id(Account, pk)
        if account is None:
            raise AccountEnvironmentError("账号不存在", code="account_not_found")
        if not account.device_id:
            raise AccountEnvironmentError("当前账号未绑定设备，无法启动隔离环境", code="device_unbound")

        device = self._repo.get_by_id(Device, account.device_id)
        if device is None:
            raise AccountEnvironmentError("当前账号绑定的设备不存在", code="device_missing")

        raw_cookie = str(account.cookie_content or "").strip()
        if not raw_cookie:
            raise AccountEnvironmentError("当前账号没有可用 Cookie，无法启动登录态环境", code="cookie_missing")

        cookie_entries = self._parse_cookie_entries(raw_cookie)
        if not cookie_entries:
            raise AccountEnvironmentError("当前账号 Cookie 格式无效，无法启动登录态环境", code="cookie_invalid")

        platform = str(account.platform or "tiktok").strip().lower() or "tiktok"
        required = _PLATFORM_AUTH_COOKIES.get(platform, set())
        names = {str(item.get("name") or "").strip().lower() for item in cookie_entries}
        if required and not (required & names):
            raise AccountEnvironmentError("当前账号缺少平台登录 Cookie，无法恢复登录态", code="cookie_auth_missing")

        opened = self._open_browser_environment(
            device,
            account=account,
            cookie_entries=cookie_entries,
            platform=platform,
        )
        self._repo.update(
            account,
            isolation_enabled=True,
            last_login_at=_dt.datetime.now(),
        )
        return opened

    def open_device_environment(self, pk: int) -> dict[str, Any]:
        device = self._repo.get_by_id(Device, pk)
        if device is None:
            raise ValueError("设备不存在")

        return self._open_browser_environment(device)

    def _open_browser_environment(
        self,
        device: Device,
        *,
        account: Account | None = None,
        cookie_entries: list[dict[str, Any]] | None = None,
        platform: str | None = None,
    ) -> dict[str, Any]:

        configured_proxy = str(device.proxy_ip or "").strip()
        if not configured_proxy:
            if account is not None:
                raise AccountEnvironmentError("当前账号绑定设备未配置代理地址，无法启动隔离环境", code="device_proxy_missing")
            raise ValueError("当前设备未配置代理地址，无法启动隔离环境")

        executable = self._resolve_browser_executable()
        if not executable:
            if account is not None:
                raise AccountEnvironmentError("未检测到可用浏览器，请安装 Edge 或 Chrome", code="browser_missing")
            raise ValueError("未检测到可用浏览器，请安装 Edge 或 Chrome")

        endpoint = self._parse_proxy_endpoint(configured_proxy)
        profile_dir = self._ensure_device_profile(device)
        relay = self._start_device_proxy_relay(device.id, endpoint)
        target_url = self._resolve_platform_home_url(platform or (account.platform if account else None))
        probe_target_url = self._resolve_platform_probe_url(platform or (account.platform if account else None))
        launcher_probe = self._start_launcher_probe(
            device.id,
            proxy_url=f"http://{relay.local_endpoint}",
            target_url=probe_target_url,
        )
        validation = self._validate_proxy_endpoint(endpoint)
        extension_dir: Path | None = None
        cookie_records: list[dict[str, Any]] = []
        session_tracker: _AccountSessionTracker | None = None
        remote_debugging_port: int | None = None
        if account is not None:
            session_tracker = self._start_account_session_tracker(account.id)
            remote_debugging_port = self._reserve_loopback_port()
            cookie_records = self._prepare_browser_cookie_records(
                cookie_entries or [],
                platform=platform or str(account.platform or "tiktok"),
            )
            try:
                extension_dir = self._write_account_cookie_extension(
                    profile_dir,
                    account,
                    cookie_records,
                    target_url=target_url,
                    report_url=session_tracker.report_url,
                    validation=self._build_extension_validation_payload(account, platform=platform),
                )
            except Exception as exc:
                raise AccountEnvironmentError(
                    f"登录态注入扩展准备失败: {exc}",
                    code="extension_prepare_failed",
                ) from exc
        launcher_path = self._write_device_proxy_launcher(
            device,
            profile_dir,
            configured_proxy=endpoint.display,
            browser_proxy=relay.local_endpoint,
            upstream_proxy=endpoint.display,
            upstream_transport=endpoint.upstream_url,
            validation=validation,
            target_url=target_url,
            account=account,
            cookie_count=len(cookie_records),
            proxy_probe_url=launcher_probe.status_url,
            session_status_url=session_tracker.status_url if session_tracker is not None else "",
        )
        launcher_url = launcher_path.as_uri()

        command = [
            executable,
            f"--user-data-dir={profile_dir}",
            "--new-window",
            "--no-first-run",
            "--no-default-browser-check",
            f"--proxy-server={relay.local_endpoint}",
        ]
        if remote_debugging_port is not None:
            command.append(f"--remote-debugging-port={remote_debugging_port}")
        if extension_dir is not None:
            command.extend([
                f"--disable-extensions-except={extension_dir}",
                f"--load-extension={extension_dir}",
            ])
        command.append(launcher_url)

        creationflags = 0
        if os.name == "nt":
            creationflags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP

        try:
            process = subprocess.Popen(command, creationflags=creationflags, close_fds=False)
        except Exception:
            self._release_device_proxy_relay(device.id)
            self._release_launcher_probe(device.id)
            if account is not None:
                raise AccountEnvironmentError("浏览器启动失败，请检查浏览器路径与扩展加载权限", code="browser_launch_failed")
            raise

        if (
            account is not None
            and session_tracker is not None
            and cookie_records
            and remote_debugging_port is not None
        ):
            self._start_account_cdp_fallback(
                account_id=account.id,
                remote_debugging_port=remote_debugging_port,
                launcher_url=launcher_url,
                cookie_records=cookie_records,
                tracker=session_tracker,
            )

        return {
            "device_id": device.id,
            "device_code": device.device_code,
            "name": device.name,
            "browser_path": executable,
            "profile_dir": str(profile_dir),
            "launcher_path": str(launcher_path),
            "launcher_url": launcher_url,
            "configured_proxy": configured_proxy,
            "configured_proxy_display": endpoint.display,
            "upstream_proxy": endpoint.display,
            "upstream_transport": endpoint.upstream_url,
            "browser_proxy": relay.local_endpoint,
            "proxy_server": relay.local_endpoint,
            "proxy_auth_present": endpoint.auth_present,
            "validation": validation,
            "launch_mode": "loopback_relay_account_session" if account is not None else "loopback_relay",
            "pid": process.pid,
            "url": target_url,
            "auto_open_delay_ms": 3000,
            "monitor_interval_ms": 10000,
            "account_id": account.id if account is not None else None,
            "account_username": account.username if account is not None else None,
            "cookie_count": len(cookie_records),
            "proxy_probe_url": launcher_probe.status_url,
            "extension_name": _ACCOUNT_SESSION_EXTENSION_NAME if account is not None else "",
            "extension_ready": bool(extension_dir) and extension_dir.exists() if account is not None else False,
            "extension_install_required": False if account is not None else False,
            "extension_install_hint": "无需手动安装，系统会在启动隔离浏览器时自动生成并加载登录扩展。" if account is not None else "",
            "extension_dir": str(extension_dir) if extension_dir is not None else "",
            "session_status_url": session_tracker.status_url if session_tracker is not None else "",
            "cdp_port": remote_debugging_port,
            "cdp_fallback_enabled": bool(remote_debugging_port) if account is not None else False,
        }

    def _normalize_device_runtime_fields(
        self,
        fields: dict[str, Any],
        *,
        existing: Device | None = None,
    ) -> dict[str, Any]:
        normalized = dict(fields)
        proxy_ip = normalized.get("proxy_ip", existing.proxy_ip if existing else None)
        fingerprint = normalized.get(
            "fingerprint_status", existing.fingerprint_status if existing else "normal"
        )

        has_proxy = bool(str(proxy_ip or "").strip())
        if "proxy_status" not in normalized:
            normalized["proxy_status"] = "online" if has_proxy else "offline"

        if "status" not in normalized:
            normalized["status"] = self._derive_device_status(
                has_proxy=has_proxy,
                fingerprint_status=str(fingerprint or "normal"),
            )

        return normalized

    def _derive_device_status(self, *, has_proxy: bool, fingerprint_status: str) -> str:
        if not has_proxy:
            return "idle"

        fingerprint_key = str(fingerprint_status or "normal").strip().lower()
        if fingerprint_key == "missing":
            return "error"
        if fingerprint_key == "drifted":
            return "warning"
        return "healthy"

    def _derive_inspected_proxy_status(self, target_host: str | None, ok: bool) -> str:
        if not target_host:
            return "offline"
        return "online" if ok else "lost"

    def _derive_inspected_device_status(
        self,
        device: Device,
        bound_accounts: Sequence[Account],
        proxy_status: str,
    ) -> str:
        fingerprint_key = str(device.fingerprint_status or "normal").strip().lower()
        if proxy_status == "offline":
            return "error" if bound_accounts else "idle"
        if proxy_status == "lost":
            return "error" if bound_accounts else "warning"
        if fingerprint_key == "missing":
            return "error"
        if fingerprint_key == "drifted":
            return "warning"
        if not bound_accounts:
            return "idle"
        has_account_risk = any(
            str(account.last_connection_status or "").lower() == "unreachable"
            or str(account.last_login_check_status or "").lower() in {"invalid", "proxy_mismatch"}
            for account in bound_accounts
        )
        if has_account_risk:
            return "warning"
        return "healthy"

    def _ensure_device_profile(self, device: Device) -> Path:
        profile_root = DATA_DIR / "browser_profiles"
        profile_root.mkdir(parents=True, exist_ok=True)
        profile_dir = profile_root / self._sanitize_device_key(device.device_code or f"device-{device.id}")
        profile_dir.mkdir(parents=True, exist_ok=True)
        manifest = {
            "device_id": device.id,
            "device_code": device.device_code,
            "name": device.name,
            "proxy_ip": device.proxy_ip,
            "region": device.region,
            "fingerprint_status": device.fingerprint_status,
            "updated_at": _dt.datetime.now().isoformat(timespec="seconds"),
        }
        (profile_dir / "tkops-profile.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return profile_dir

    def _write_device_proxy_launcher(
        self,
        device: Device,
        profile_dir: Path,
        *,
        configured_proxy: str,
        browser_proxy: str,
        upstream_proxy: str,
        upstream_transport: str,
        validation: dict[str, Any],
        target_url: str,
        account: Account | None = None,
        cookie_count: int = 0,
        proxy_probe_url: str = "",
        session_status_url: str = "",
    ) -> Path:
        launcher_path = profile_dir / "tkops-proxy-launcher.html"
        launcher_data = {
            "deviceName": device.name,
            "deviceCode": device.device_code,
            "region": device.region or "",
            "configuredProxy": configured_proxy,
            "browserProxy": browser_proxy,
            "upstreamProxy": upstream_proxy,
            "upstreamTransport": upstream_transport,
            "validation": validation,
            "targetUrl": target_url,
            "checkTarget": self._resolve_platform_probe_url(account.platform if account is not None else None),
            "startedAt": _dt.datetime.now().isoformat(timespec="seconds"),
            "profileDir": str(profile_dir),
            "proxyProbeUrl": proxy_probe_url,
            "autoOpenDelayMs": 3000,
            "monitorIntervalMs": 10000,
            "accountUsername": account.username if account is not None else "",
            "cookieCount": int(cookie_count or 0),
            "extensionName": _ACCOUNT_SESSION_EXTENSION_NAME if account is not None else "",
            "extensionInstallHint": "无需手动安装，系统会在启动隔离浏览器时自动加载登录扩展。" if account is not None else "",
            "sessionStatusUrl": session_status_url,
        }
        launcher_json = json.dumps(launcher_data, ensure_ascii=False)
        page = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TKOPS 代理自检 / {device.device_code}</title>
  <style>
    body {{
      margin: 0;
      padding: 24px;
      font-family: "Microsoft YaHei", sans-serif;
      background: linear-gradient(180deg, #f6f9ff 0%, #eef3f9 100%);
      color: #16324f;
    }}
    .shell {{ max-width: 1080px; margin: 0 auto; }}
    .card {{
      background: #fff;
      border: 1px solid #d7e2f0;
      border-radius: 18px;
      box-shadow: 0 12px 40px rgba(22, 50, 79, 0.08);
      padding: 20px;
      margin-bottom: 18px;
    }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 18px; }}
    .kv {{ display: grid; grid-template-columns: 128px 1fr; gap: 10px 12px; margin-bottom: 10px; }}
    .key {{ color: #5f748c; }}
    .value {{ font-weight: 700; word-break: break-all; }}
    .mono {{ font-family: Consolas, monospace; }}
    .pill {{
      display: inline-block;
      padding: 8px 14px;
      border-radius: 999px;
      font-weight: 700;
      background: #fff8ea;
      color: #b66a00;
      border: 1px solid rgba(182, 106, 0, 0.28);
    }}
    .pill.ok {{ background: rgba(31, 143, 88, 0.08); color: #1f8f58; border-color: rgba(31, 143, 88, 0.28); }}
    .pill.error {{ background: rgba(200, 59, 59, 0.08); color: #c83b3b; border-color: rgba(200, 59, 59, 0.28); }}
    .banner {{
      display: none;
      margin-top: 14px;
      padding: 14px 16px;
      border-radius: 14px;
      font-weight: 700;
    }}
    .banner.show {{ display: block; }}
    .banner.ok {{ color: #1f8f58; background: rgba(31, 143, 88, 0.10); }}
    .banner.warn {{ color: #b66a00; background: rgba(182, 106, 0, 0.10); }}
    .banner.error {{ color: #c83b3b; background: rgba(200, 59, 59, 0.10); }}
    .actions {{ display: flex; gap: 12px; flex-wrap: wrap; margin-top: 16px; }}
    button {{
      border: 0;
      border-radius: 12px;
      padding: 12px 18px;
      font-size: 14px;
      font-weight: 700;
      cursor: pointer;
      background: #1f6feb;
      color: #fff;
    }}
    button.secondary {{ background: #edf4ff; color: #1f6feb; border: 1px solid rgba(31, 111, 235, 0.2); }}
    button:disabled {{ cursor: not-allowed; opacity: 0.55; }}
  </style>
</head>
<body>
  <div class="shell">
    <section class="card">
      <h1 style="margin:0 0 8px;">代理自检页</h1>
      <p style="margin:0;color:#5f748c;line-height:1.7;">当前浏览器实例只使用本机 loopback relay。自检通过后再打开 TikTok；如果代理失效，本页会关闭由它打开的 TikTok 标签并提示原因。</p>
      <div style="margin-top:18px;display:flex;gap:12px;flex-wrap:wrap;">
        <div id="statusPill" class="pill">正在检测代理</div>
        <div class="pill mono">{browser_proxy}</div>
      </div>
      <div id="statusBanner" class="banner"></div>
    </section>

    <div class="grid">
      <section class="card">
        <h2 style="margin:0 0 14px;">实例信息</h2>
        <div class="kv"><div class="key">设备名称</div><div class="value">{device.name}</div></div>
        <div class="kv"><div class="key">设备编码</div><div class="value mono">{device.device_code}</div></div>
        <div class="kv"><div class="key">设备地区</div><div class="value">{device.region or "-"}</div></div>
                <div class="kv"><div class="key">账号登录态</div><div class="value">{account.username if account is not None else "未注入账号 Cookie"}</div></div>
                <div class="kv"><div class="key">Cookie 注入</div><div class="value">{cookie_count if account is not None else 0} 条</div></div>
            <div class="kv"><div class="key">登录扩展</div><div class="value">{_ACCOUNT_SESSION_EXTENSION_NAME if account is not None else "未启用"}</div></div>
            <div class="kv"><div class="key">手动安装</div><div class="value">{("不需要，系统随浏览器自动加载" if account is not None else "不适用")}</div></div>
        <div class="kv"><div class="key">独立 Profile</div><div class="value mono">{profile_dir}</div></div>
        <div class="kv"><div class="key">启动时间</div><div class="value">{launcher_data["startedAt"]}</div></div>
      </section>

      <section class="card">
        <h2 style="margin:0 0 14px;">代理信息</h2>
        <div class="kv"><div class="key">设备配置代理</div><div class="value mono">{configured_proxy}</div></div>
        <div class="kv"><div class="key">浏览器启动代理</div><div class="value mono">{browser_proxy}</div></div>
        <div class="kv"><div class="key">上游代理</div><div class="value mono">{upstream_proxy}</div></div>
        <div class="kv"><div class="key">当前出口 IP</div><div id="egressIp" class="value mono">检测中</div></div>
        <div class="kv"><div class="key">最近检测</div><div id="checkedAt" class="value">尚未完成</div></div>
        <div class="kv"><div class="key">TikTok 探测</div><div id="targetCheck" class="value">待检测</div></div>
                <div class="kv"><div class="key">登录态校验</div><div id="sessionCheck" class="value">{('等待扩展注入' if account is not None else '未启用')}</div></div>
      </section>
    </div>

    <section class="card">
      <h2 style="margin:0 0 14px;">操作</h2>
      <div class="actions">
        <button id="openTarget" type="button" disabled>请先完成检测</button>
        <button id="recheck" type="button" class="secondary">立即重新检测</button>
      </div>
                        <div id="autoOpenHint" style="margin-top:12px;color:#5f748c;line-height:1.7;">检测通过后，按钮会在 3 秒倒计时结束后开放，用来避免“刚通过又立刻掉线”的误操作。{('当前实例已随浏览器自动加载登录扩展，无需手动安装；打开 TikTok 后会尝试直接恢复登录态。' if account is not None else '')}</div>
    </section>
  </div>

  <script>
    const launcher = {launcher_json};
    const statusPill = document.getElementById('statusPill');
    const statusBanner = document.getElementById('statusBanner');
    const openTargetBtn = document.getElementById('openTarget');
    const recheckBtn = document.getElementById('recheck');
    const egressIpEl = document.getElementById('egressIp');
    const checkedAtEl = document.getElementById('checkedAt');
    const targetCheckEl = document.getElementById('targetCheck');
    const sessionCheckEl = document.getElementById('sessionCheck');
    const autoOpenHint = document.getElementById('autoOpenHint');
    let targetWindow = null;
    let proxyHealthy = false;
    let sessionHealthy = !launcher.accountUsername;
    let sessionPolled = !launcher.accountUsername;
    let sessionLoginStatus = launcher.accountUsername ? 'pending' : 'valid';
    let sessionAppliedCount = 0;
    let autoOpenedTarget = false;
    let countdownTimer = null;
    let currentCountdown = 0;

    function setStatus(kind, title, detail) {{
      statusPill.className = 'pill ' + (kind || '');
      statusPill.textContent = title;
      statusBanner.className = 'banner show ' + kind;
      statusBanner.textContent = detail || '';
      document.title = '[' + title + '] ' + launcher.deviceCode + ' / ' + launcher.browserProxy;
    }}

    function stopCountdown() {{
      if (countdownTimer) {{
        window.clearInterval(countdownTimer);
        countdownTimer = null;
      }}
      currentCountdown = 0;
    }}

    function setOpenButton(enabled, label) {{
      openTargetBtn.disabled = !enabled;
      openTargetBtn.textContent = label || (enabled ? '立即打开 TikTok' : '请先完成检测');
    }}

        function openTarget(trigger) {{
            if (!proxyHealthy) return;
            if (targetWindow && !targetWindow.closed) return;
            targetWindow = window.open(launcher.targetUrl, 'tkops_target');
            if (!targetWindow) {{
                autoOpenedTarget = false;
                if (trigger === 'auto') {{
                    setOpenButton(true, sessionHealthy ? '立即进入 TikTok' : '打开 TikTok 检查登录');
                    autoOpenHint.textContent = '浏览器拦截了自动打开新标签，请点击按钮手动进入 TikTok。';
                }} else {{
                    alert('浏览器拦截了新标签，请允许当前页面打开新标签后重试。');
                }}
                return;
            }}
            setStatus('ok', '代理可用', sessionHealthy ? '已自动打开 TikTok，并保持当前页继续监控登录状态。' : 'TikTok 已打开，可直接在目标页确认登录状态或继续登录。');
        }}

        function tryAutoOpenTarget() {{
            if (!launcher.accountUsername || autoOpenedTarget || !proxyHealthy || !sessionHealthy) return;
            autoOpenedTarget = true;
            setOpenButton(false, '正在自动进入 TikTok');
            autoOpenHint.textContent = '登录态已通过校验，正在自动打开 TikTok。';
            window.setTimeout(function () {{
                openTarget('auto');
            }}, 600);
        }}

        function refreshOpenGate() {{
            stopCountdown();
            if (!proxyHealthy) {{
                setOpenButton(false, '请先完成代理检测');
                return;
            }}
            if (launcher.accountUsername) {{
                if (!sessionPolled) {{
                                        setOpenButton(true, '进入 TikTok 并等待注入');
                                        autoOpenHint.textContent = '代理已通过，扩展正在后台注入 Cookie；你现在就可以进入 TikTok，注入结果会继续回报到本页。';
                    return;
                }}
                                if (sessionHealthy) {{
                                        autoOpenHint.textContent = '代理检测与登录态校验均已通过，系统会自动打开 TikTok。';
                                        tryAutoOpenTarget();
                    return;
                }}
                                if (sessionLoginStatus === 'invalid') {{
                                        setOpenButton(true, '打开 TikTok 并重新登录');
                                        autoOpenHint.textContent = 'Cookie 已注入，但平台没有确认登录态；可以直接打开 TikTok 在该隔离环境里重新登录。';
                                        return;
                                }}
                                if (sessionAppliedCount > 0) {{
                                        setOpenButton(true, '打开 TikTok 检查登录');
                                        autoOpenHint.textContent = 'Cookie 已写入浏览器，但平台接口还没有返回明确结果；可以直接进入 TikTok 观察是否已恢复登录。';
                                        return;
                                }}
                                setOpenButton(true, '进入 TikTok');
                                autoOpenHint.textContent = '代理已通过，但扩展还没有回报写入结果；可以先进入 TikTok，当前页会继续轮询状态。';
                                return;
            }}
            startCountdown();
        }}

    function startCountdown() {{
      stopCountdown();
      currentCountdown = Math.max(0, Math.floor(Number(launcher.autoOpenDelayMs || 3000) / 1000));
      if (!currentCountdown) {{
        setOpenButton(true, '立即打开 TikTok');
        autoOpenHint.textContent = '自检已通过，当前按钮可直接打开 TikTok。';
        return;
      }}
      setOpenButton(false, currentCountdown + ' 秒后可打开 TikTok');
      autoOpenHint.textContent = '自检通过，倒计时结束后才会开放打开按钮。';
      countdownTimer = window.setInterval(function () {{
        currentCountdown -= 1;
        if (currentCountdown <= 0) {{
          stopCountdown();
          setOpenButton(true, '立即打开 TikTok');
          autoOpenHint.textContent = '自检已通过，当前按钮可直接打开 TikTok。';
          return;
        }}
        setOpenButton(false, currentCountdown + ' 秒后可打开 TikTok');
      }}, 1000);
    }}

    function renderPrecheck() {{
      const validation = launcher.validation || {{}};
      if (validation.ok) {{
        setStatus('ok', '代理预检通过', validation.detail || '上游代理已连通');
        egressIpEl.textContent = validation.egress_ip || '未知';
        targetCheckEl.textContent = '预检通过';
        proxyHealthy = true;
                refreshOpenGate();
      }} else {{
        setStatus('error', '代理预检失败', validation.message || '上游代理不可用');
        egressIpEl.textContent = '不可达';
        targetCheckEl.textContent = '预检失败';
        proxyHealthy = false;
        setOpenButton(false);
        autoOpenHint.textContent = validation.detail ? ('失败原因：' + validation.detail) : '检测失败时不会开放 TikTok。';
      }}
    }}

    async function detectProxy() {{
      recheckBtn.disabled = true;
      stopCountdown();
      setOpenButton(false);
      setStatus('warn', '正在检测代理', '正在验证上游代理连通性、认证信息和 TikTok 可达性');
      try {{
                if (!launcher.proxyProbeUrl) throw new Error('当前实例未提供代理探针地址');
                const probeResp = await fetch(launcher.proxyProbeUrl + '?_=' + Date.now(), {{ cache: 'no-store' }});
                if (!probeResp.ok) throw new Error('代理探针不可用：HTTP ' + probeResp.status);
                const probe = await probeResp.json();
                const egressIp = probe && probe.egress_ip ? probe.egress_ip : '';
                checkedAtEl.textContent = probe && probe.checked_at ? new Date(probe.checked_at).toLocaleString() : new Date().toLocaleString();
                if (!probe || !probe.ok) throw new Error((probe && (probe.message || probe.detail)) || '代理探测失败');
        if (!egressIp) throw new Error('出口 IP 探测结果为空');
        egressIpEl.textContent = egressIp;

                const targetOk = probe && typeof probe.target_ok === 'boolean' ? probe.target_ok : null;
                const targetStatus = probe && probe.target_status_code ? probe.target_status_code : null;
                if (targetOk === true) targetCheckEl.textContent = 'TikTok 探测通过';
                else if (targetOk === false) targetCheckEl.textContent = targetStatus ? ('TikTok 探测异常 / HTTP ' + targetStatus) : 'TikTok 探测异常';
                else targetCheckEl.textContent = 'TikTok 探测未启用';
        proxyHealthy = true;
                if (targetOk === false) {{
                    setStatus('warn', '子代理可用', (probe && probe.detail) || '代理出口已建立，但 TikTok 探测未得到稳定结果。');
                    autoOpenHint.textContent = '子代理已建立，虽然 TikTok 探测未稳定通过，但你已经可以直接进入 TikTok 验证注入和登录态。';
                }} else {{
                    setStatus('ok', '子代理可用', (probe && probe.detail) || '当前浏览器实例通过本机子代理访问上游代理，认证信息未暴露到命令行。');
                }}
                refreshOpenGate();
      }} catch (error) {{
            proxyHealthy = false;
            if (!String(egressIpEl.textContent || '').trim() || egressIpEl.textContent === '检测中') egressIpEl.textContent = '不可达';
        targetCheckEl.textContent = 'TikTok 探测失败';
            setStatus('error', '子代理检测失败', String(error && error.message ? error.message : error));
            autoOpenHint.textContent = '当前子代理还没有建立成功，暂时不能判断 TikTok 注入是否生效。请先修复代理链路后再试。';
        if (targetWindow && !targetWindow.closed) {{
          try {{
            targetWindow.close();
          }} catch (_ignored) {{}}
          targetWindow = null;
          alert('代理已失效，当前打开的 TikTok 标签已关闭。请修复代理后重新检测。');
        }}
      }} finally {{
        recheckBtn.disabled = false;
      }}
    }}

        async function pollSessionStatus() {{
            if (!launcher.sessionStatusUrl) return;
            try {{
                const response = await fetch(launcher.sessionStatusUrl + '?_=' + Date.now(), {{ cache: 'no-store' }});
                if (!response.ok) throw new Error('HTTP ' + response.status);
                const payload = await response.json();
                sessionPolled = true;
                const loginStatus = String(payload.loginStatus || payload.status || 'pending');
                const failed = Array.isArray(payload.failed) ? payload.failed : [];
                sessionLoginStatus = loginStatus;
                sessionAppliedCount = Number(payload.appliedCount || 0);
                if (sessionCheckEl) {{
                    if (loginStatus === 'valid') sessionCheckEl.textContent = '已通过真实登录校验';
                    else if (loginStatus === 'invalid') sessionCheckEl.textContent = 'Cookie 已注入，但登录态无效';
                    else if (loginStatus === 'error') sessionCheckEl.textContent = '登录校验失败';
                    else if (sessionAppliedCount > 0) sessionCheckEl.textContent = 'Cookie 已注入，等待平台返回最终结果';
                    else sessionCheckEl.textContent = payload.message || '等待系统自动加载登录扩展';
                }}
                sessionHealthy = loginStatus === 'valid';
                if (!sessionHealthy && launcher.accountUsername) {{
                    const failMessage = failed.length ? ('失败 Cookie：' + failed.map(function (item) {{ return item.name || 'unknown'; }}).join('、')) : '';
                    autoOpenHint.textContent = (payload.message || '登录态尚未恢复。') + (failMessage ? ('；' + failMessage) : '');
                }}
                refreshOpenGate();
            }} catch (_error) {{
                sessionPolled = false;
                sessionHealthy = false;
                if (sessionCheckEl) sessionCheckEl.textContent = '等待系统自动加载登录扩展回报';
            }}
        }}

    openTargetBtn.addEventListener('click', function () {{
      if (!proxyHealthy) {{
        alert('当前代理尚未通过检测，暂时不能打开 TikTok。');
        return;
      }}
            openTarget('manual');
    }});

    recheckBtn.addEventListener('click', function () {{
      detectProxy();
            if (launcher.accountUsername) pollSessionStatus();
    }});

    renderPrecheck();
    detectProxy();
        if (launcher.accountUsername && launcher.sessionStatusUrl) {{
            pollSessionStatus();
            window.setInterval(pollSessionStatus, 1500);
        }}
    window.setInterval(detectProxy, Number(launcher.monitorIntervalMs || 10000));
  </script>
</body>
</html>
"""
        launcher_path.write_text(page, encoding="utf-8")
        return launcher_path

    def _resolve_platform_home_url(self, platform: str | None) -> str:
        key = str(platform or "tiktok").strip().lower() or "tiktok"
        return _PLATFORM_HOME_URLS.get(key, _PLATFORM_HOME_URLS["tiktok"])

    def _resolve_platform_probe_url(self, platform: str | None) -> str:
        key = str(platform or "tiktok").strip().lower() or "tiktok"
        if key in {"tiktok", "tiktok_shop"}:
            return "https://www.tiktok.com/favicon.ico"
        if key == "instagram":
            return "https://www.instagram.com/favicon.ico"
        return self._resolve_platform_home_url(platform)

    def _default_cookie_domain_for_platform(self, platform: str | None) -> str:
        key = str(platform or "tiktok").strip().lower() or "tiktok"
        return _PLATFORM_DEFAULT_COOKIE_DOMAINS.get(key, _PLATFORM_DEFAULT_COOKIE_DOMAINS["tiktok"])

    def _prepare_browser_cookie_records(
        self,
        cookie_entries: list[dict[str, Any]],
        *,
        platform: str | None,
    ) -> list[dict[str, Any]]:
        default_domain = self._default_cookie_domain_for_platform(platform)
        records: list[dict[str, Any]] = []
        for cookie in cookie_entries:
            name = str(cookie.get("name") or "").strip()
            if not name:
                continue
            domain = str(cookie.get("domain") or default_domain).strip() or default_domain
            path = str(cookie.get("path") or "/").strip() or "/"
            secure = self._cookie_flag(cookie.get("secure"), default=True)
            http_only = self._cookie_flag(cookie.get("httpOnly"), default=False)
            same_site = self._normalize_extension_same_site(cookie.get("sameSite"))
            record = {
                "url": self._cookie_url_for_domain(domain, path=path, secure=secure),
                "domain": domain,
                "path": path,
                "name": name,
                "value": str(cookie.get("value") or ""),
                "secure": secure,
                "httpOnly": http_only,
            }
            expires_at = self._resolve_cookie_expiry(cookie)
            if expires_at is not None:
                record["expirationDate"] = int(expires_at / 1000)
            if same_site is not None:
                record["sameSite"] = same_site
            records.append(record)
        return records

    def _write_account_cookie_extension(
        self,
        profile_dir: Path,
        account: Account,
        cookie_records: list[dict[str, Any]],
        *,
        target_url: str,
        report_url: str,
        validation: dict[str, Any],
    ) -> Path:
        for stale_dir in profile_dir.glob("tkops-account-session-extension*"):
            if stale_dir.is_dir():
                shutil.rmtree(stale_dir, ignore_errors=True)

        extension_suffix = _dt.datetime.now().strftime("%Y%m%d%H%M%S%f")
        extension_dir = profile_dir / f"tkops-account-session-extension-{account.id}-{extension_suffix}"
        extension_dir.mkdir(parents=True, exist_ok=True)

        permissions = sorted(self._build_cookie_host_permissions(cookie_records, target_url=target_url))
        report_permission = self._host_permission_for_url(report_url)
        if report_permission not in permissions:
            permissions.append(report_permission)
            permissions.sort()
        manifest = {
            "manifest_version": 3,
            "name": f"{_ACCOUNT_SESSION_EXTENSION_NAME} / {account.username or account.id}",
            "version": "1.0.0",
            "permissions": ["cookies", "storage", "alarms", "tabs"],
            "host_permissions": permissions,
            "background": {"service_worker": "background.js"},
            "minimum_chrome_version": "120",
        }
        payload = {
            "accountId": account.id,
            "username": account.username,
            "targetUrl": target_url,
            "cookies": cookie_records,
                        "reportUrl": report_url,
                        "validation": validation,
        }
        background = """
const payload = __PAYLOAD__;
const RETRY_ALARM = 'tkops-cookie-retry';
const RETRY_DELAY_MINUTES = 1;
let applyInFlight = null;

async function reportState(partial) {
    if (!payload.reportUrl) return;
    try {
        await fetch(payload.reportUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(partial || {}),
        });
    } catch (_error) {
        // ignore report failures; launcher will continue polling
    }
}

function extractTikTokIdentity(payload) {
    const queue = [payload];
    const visited = new Set();
    const keys = ['username', 'user_name', 'userName', 'unique_id', 'uniqueId', 'screen_name', 'screenName', 'nickname', 'nick_name', 'display_name', 'displayName', 'user_id', 'userId', 'user_id_str', 'uid', 'uid_str'];
    while (queue.length) {
        const candidate = queue.shift();
        if (!candidate || typeof candidate !== 'object') continue;
        if (visited.has(candidate)) continue;
        visited.add(candidate);
        for (const key of keys) {
            if (candidate[key] !== undefined && candidate[key] !== null && candidate[key] !== '') {
                return String(candidate[key]).trim();
            }
        }
        for (const value of Object.values(candidate)) {
            if (value && typeof value === 'object' && !Array.isArray(value)) queue.push(value);
        }
    }
    return '';
}

function payloadIndicatesInvalidLogin(payload) {
    if (!payload || typeof payload !== 'object') return false;
    const texts = [];
    const queue = [payload];
    const visited = new Set();
    while (queue.length) {
        const candidate = queue.shift();
        if (!candidate || typeof candidate !== 'object') continue;
        if (visited.has(candidate)) continue;
        visited.add(candidate);
        for (const key of ['message', 'status_msg', 'error_message', 'description', 'detail']) {
            if (candidate[key]) texts.push(String(candidate[key]).toLowerCase());
        }
        for (const value of Object.values(candidate)) {
            if (value && typeof value === 'object') queue.push(value);
        }
    }
    const text = texts.join(' ');
    return [
        'not login',
        'not logged',
        'login_required',
        'login expired',
        'session expired',
        'unauthorized',
        'challenge_required',
        'checkpoint_required',
        'captcha',
        'verify',
        'verification',
        'please login',
        'please log in',
        '请登录',
        '未登录',
        '登录已过期',
        '挑战',
        '验证码',
        '验证',
        '风控',
    ].some((marker) => text.includes(marker));
}

function targetHostCandidates() {
    const hosts = new Set();
    try {
        const url = new URL(String(payload.targetUrl || ''));
        if (url.hostname) hosts.add(url.hostname);
        const withoutWww = url.hostname.replace(/^www\./, '');
        if (withoutWww) hosts.add(withoutWww);
    } catch (_error) {
        // ignore malformed target url
    }
    for (const cookie of payload.cookies || []) {
        const domain = String((cookie && cookie.domain) || '').trim().replace(/^\./, '');
        if (domain) hosts.add(domain);
    }
    return Array.from(hosts);
}

function matchesTargetUrl(url) {
    if (!url) return false;
    try {
        const parsed = new URL(url);
        const host = parsed.hostname;
        return targetHostCandidates().some((candidate) => host === candidate || host.endsWith('.' + candidate));
    } catch (_error) {
        return false;
    }
}

async function setRetryAlarm(reason) {
    await chrome.alarms.clear(RETRY_ALARM);
    await chrome.alarms.create(RETRY_ALARM, { delayInMinutes: RETRY_DELAY_MINUTES });
    await reportState({
        status: 'retry_scheduled',
        loginStatus: 'pending',
        message: '登录扩展将在稍后自动重试注入',
        retryReason: reason || '',
    });
}

async function clearRetryAlarm() {
    await chrome.alarms.clear(RETRY_ALARM);
}

async function nextAttemptMeta(trigger) {
    const stored = await chrome.storage.local.get(['tkopsSessionMeta']);
    const current = stored && stored.tkopsSessionMeta ? stored.tkopsSessionMeta : {};
    const attemptCount = Number(current.attemptCount || 0) + 1;
    const meta = {
        attemptCount,
        lastTrigger: String(trigger || 'unknown'),
        lastAttemptAt: new Date().toISOString(),
    };
    await chrome.storage.local.set({ tkopsSessionMeta: meta });
    return meta;
}

async function validateLoginState() {
    const validation = payload.validation || {};
    const requests = Array.isArray(validation.requests) ? validation.requests : [];
    if (!requests.length) {
        return { loginStatus: 'unknown', message: '当前平台未配置浏览器侧登录校验' };
    }
    const reasons = [];
    for (const request of requests) {
        try {
            const response = await fetch(request.url, {
                method: 'GET',
                headers: request.headers || {},
                credentials: 'include',
                cache: 'no-store',
            });
            const contentType = String(response.headers.get('content-type') || '').toLowerCase();
            const payloadData = contentType.includes('json') ? await response.json().catch(() => ({})) : {};
            if (response.status === 401 || response.status === 403 || payloadIndicatesInvalidLogin(payloadData)) {
                const detail = (payloadData && (payloadData.message || payloadData.status_msg || payloadData.error_message || payloadData.description || payloadData.detail)) || ('HTTP ' + response.status);
                return { loginStatus: 'invalid', message: '浏览器侧登录校验失败：' + detail, target: request.url, httpStatus: response.status };
            }
            const identity = request.type === 'tiktok' ? extractTikTokIdentity(payloadData) : '';
            if (identity) {
                return { loginStatus: 'valid', message: '已通过浏览器侧真实接口确认登录态：' + identity, target: request.url, httpStatus: response.status };
            }
            reasons.push(response.status + '/' + (contentType || 'unknown'));
        } catch (error) {
            reasons.push(String(error && error.message ? error.message : error));
        }
    }
    return { loginStatus: 'unknown', message: '浏览器侧无法确认登录态：' + reasons.join('；') };
}

async function runApplySessionCookies(trigger) {
    const meta = await nextAttemptMeta(trigger);
    await reportState({
        status: 'applying',
        loginStatus: 'pending',
        message: '正在注入账号 Cookie',
        trigger: meta.lastTrigger,
        attemptCount: meta.attemptCount,
    });

    const applied = [];
    const failed = [];
    for (const cookie of payload.cookies || []) {
        const details = {
            url: cookie.url,
            name: cookie.name,
            value: cookie.value,
            path: cookie.path || '/',
            secure: !!cookie.secure,
            httpOnly: !!cookie.httpOnly,
        };
        if (cookie.domain) details.domain = cookie.domain;
        if (cookie.sameSite) details.sameSite = cookie.sameSite;
        if (cookie.expirationDate) details.expirationDate = cookie.expirationDate;
        try {
            const result = await chrome.cookies.set(details);
            applied.push((result && result.name) || cookie.name);
        } catch (error) {
            failed.push({ name: cookie.name, message: String(error && error.message ? error.message : error) });
        }
    }

    const validation = await validateLoginState();
    const shouldRetry = validation.loginStatus !== 'valid' || failed.length > 0;
    if (shouldRetry) {
        await setRetryAlarm(validation.message || '登录态尚未恢复');
    } else {
        await clearRetryAlarm();
    }

    await chrome.storage.local.set({
        tkopsSession: {
            accountId: payload.accountId,
            username: payload.username,
            targetUrl: payload.targetUrl,
            appliedCount: applied.length,
            failed,
            loginStatus: validation.loginStatus,
            validationMessage: validation.message,
            validationTarget: validation.target || '',
            validationHttpStatus: validation.httpStatus || null,
            trigger: meta.lastTrigger,
            attemptCount: meta.attemptCount,
            retryScheduled: shouldRetry,
            updatedAt: new Date().toISOString(),
        },
      });

    await reportState({
        status: validation.loginStatus === 'valid' ? 'ready' : (failed.length ? 'partial' : 'ready'),
        loginStatus: validation.loginStatus,
        appliedCount: applied.length,
        failed,
        message: validation.message,
        target: validation.target || '',
        httpStatus: validation.httpStatus || null,
        trigger: meta.lastTrigger,
        attemptCount: meta.attemptCount,
        retryScheduled: shouldRetry,
    });
}

function applySessionCookies(trigger) {
    if (applyInFlight) return applyInFlight;
    applyInFlight = runApplySessionCookies(trigger).finally(() => {
        applyInFlight = null;
    });
    return applyInFlight;
}

chrome.runtime.onInstalled.addListener(() => { void applySessionCookies('installed'); });
chrome.runtime.onStartup.addListener(() => { void applySessionCookies('startup'); });
chrome.alarms.onAlarm.addListener((alarm) => {
    if (alarm && alarm.name === RETRY_ALARM) void applySessionCookies('alarm');
});
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    const candidateUrl = String((changeInfo && changeInfo.url) || (tab && tab.url) || '');
    if (!candidateUrl || !matchesTargetUrl(candidateUrl)) return;
    if (changeInfo && changeInfo.status && changeInfo.status !== 'complete') return;
    void applySessionCookies('tab_updated');
});
void reportState({ status: 'booting', loginStatus: 'pending', message: '登录扩展已加载，准备注入账号 Cookie' });
void applySessionCookies('boot');
""".replace("__PAYLOAD__", json.dumps(payload, ensure_ascii=False))

        (extension_dir / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (extension_dir / "background.js").write_text(background, encoding="utf-8")
        return extension_dir

    def _build_cookie_host_permissions(
        self,
        cookie_records: list[dict[str, Any]],
        *,
        target_url: str,
    ) -> set[str]:
        permissions = {self._host_permission_for_url(target_url)}
        for cookie in cookie_records:
            permissions.add(self._host_permission_for_url(str(cookie.get("url") or target_url)))
        return permissions

    def _build_extension_validation_payload(self, account: Account, *, platform: str | None) -> dict[str, Any]:
        platform_key = str(platform or account.platform or "tiktok").strip().lower() or "tiktok"
        if platform_key in {"tiktok", "tiktok_shop"}:
            region = str(account.region or "US").upper()
            return {
                "platform": platform_key,
                "requests": [
                    {
                        "type": "tiktok",
                        "url": (
                            "https://www.tiktok.com/passport/web/account/info/"
                            f"?aid=1459&app_language=zh-Hans&language=zh-Hans&region={quote(region, safe='')}"
                        ),
                        "headers": {
                            "accept": "application/json, text/plain, */*",
                            "referer": "https://www.tiktok.com/",
                            "x-requested-with": "XMLHttpRequest",
                        },
                    },
                    {
                        "type": "tiktok",
                        "url": (
                            "https://www.tiktok.com/api/me/"
                            f"?aid=1988&app_language=zh-Hans&language=zh-Hans&region={quote(region, safe='')}"
                        ),
                        "headers": {
                            "accept": "application/json, text/plain, */*",
                            "referer": "https://www.tiktok.com/",
                            "x-requested-with": "XMLHttpRequest",
                        },
                    },
                ],
            }
        return {"platform": platform_key, "requests": []}

    def _release_account_session_tracker(self, account_id: int) -> None:
        tracker = self._account_session_trackers.pop(int(account_id), None)
        if tracker is not None:
            tracker.close()

    def _start_account_session_tracker(self, account_id: int) -> _AccountSessionTracker:
        self._release_account_session_tracker(account_id)
        tracker = _AccountSessionTracker(account_id)
        self._account_session_trackers[int(account_id)] = tracker
        return tracker

    def _host_permission_for_url(self, url: str) -> str:
        parts = urlsplit(str(url or "https://www.tiktok.com/"))
        host = parts.hostname or "www.tiktok.com"
        return f"{parts.scheme or 'https'}://{host}/*"

    def _cookie_url_for_domain(self, domain: str, *, path: str = "/", secure: bool = True) -> str:
        host = str(domain or "").strip().lstrip(".") or self._default_cookie_domain_for_platform("tiktok").lstrip(".")
        normalized_path = path if str(path or "/").startswith("/") else "/" + str(path)
        scheme = "https" if secure else "http"
        return f"{scheme}://{host}{normalized_path}"

    def _cookie_flag(self, value: Any, *, default: bool) -> bool:
        if value is None or value == "":
            return default
        if isinstance(value, bool):
            return value
        normalized = str(value).strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off"}:
            return False
        return default

    def _normalize_extension_same_site(self, value: Any) -> str | None:
        if value in (None, ""):
            return None
        normalized = str(value).strip().lower().replace("-", "_")
        mapping = {
            "lax": "lax",
            "strict": "strict",
            "none": "no_restriction",
            "no_restriction": "no_restriction",
            "unspecified": "unspecified",
        }
        return mapping.get(normalized)

    def _resolve_browser_executable(self) -> str | None:
        candidates = [
            self._repo.get_setting("browser.executable_path", "").strip(),
            shutil.which("msedge"),
            shutil.which("chrome"),
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
        for item in candidates:
            if item and Path(item).exists():
                return str(Path(item))
        return None

    def _reserve_loopback_port(self) -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            sock.listen(1)
            return int(sock.getsockname()[1])

    def _start_account_cdp_fallback(
        self,
        *,
        account_id: int,
        remote_debugging_port: int,
        launcher_url: str,
        cookie_records: list[dict[str, Any]],
        tracker: _AccountSessionTracker,
    ) -> None:
        thread = threading.Thread(
            target=self._run_account_cdp_fallback,
            name=f"tkops-account-cdp-{account_id}",
            daemon=True,
            kwargs={
                "remote_debugging_port": remote_debugging_port,
                "launcher_url": launcher_url,
                "cookie_records": [dict(item) for item in cookie_records],
                "tracker": tracker,
            },
        )
        thread.start()

    def _run_account_cdp_fallback(
        self,
        *,
        remote_debugging_port: int,
        launcher_url: str,
        cookie_records: list[dict[str, Any]],
        tracker: _AccountSessionTracker,
    ) -> None:
        try:
            tracker.update({
                "status": "cdp_pending",
                "loginStatus": "pending",
                "message": "正在等待浏览器调试端口，准备执行 CDP Cookie 回退注入",
                "cdpPort": remote_debugging_port,
            })
            websocket_url = self._wait_for_cdp_target_websocket(
                remote_debugging_port=remote_debugging_port,
                launcher_url=launcher_url,
            )
            applied, failed = self._cdp_set_cookies(websocket_url, cookie_records)
            tracker.update({
                "status": "cdp_applied",
                "loginStatus": "pending",
                "appliedCount": len(applied),
                "failed": failed,
                "message": (
                    f"已通过 CDP 回退注入 {len(applied)} 条 Cookie，等待扩展或页面完成登录校验"
                    if not failed else
                    f"CDP 已注入 {len(applied)} 条 Cookie，另有 {len(failed)} 条失败"
                ),
                "cdpPort": remote_debugging_port,
            })
        except Exception as exc:
            tracker.update({
                "status": "cdp_failed",
                "loginStatus": "pending",
                "message": f"CDP 回退注入未完成：{exc}",
                "cdpPort": remote_debugging_port,
            })

    def _wait_for_cdp_target_websocket(
        self,
        *,
        remote_debugging_port: int,
        launcher_url: str,
        timeout: float = 15.0,
    ) -> str:
        deadline = time.time() + timeout
        endpoint = f"http://127.0.0.1:{remote_debugging_port}/json/list"
        while time.time() < deadline:
            try:
                with httpx.Client(timeout=1.5) as client:
                    response = client.get(endpoint)
                    response.raise_for_status()
                    payload = response.json()
            except Exception:
                time.sleep(0.25)
                continue
            if isinstance(payload, list):
                for item in payload:
                    if not isinstance(item, dict) or item.get("type") != "page":
                        continue
                    current_url = str(item.get("url") or "")
                    if current_url == launcher_url or "tkops-proxy-launcher.html" in current_url:
                        websocket_url = str(item.get("webSocketDebuggerUrl") or "").strip()
                        if websocket_url:
                            return websocket_url
            time.sleep(0.25)
        raise TimeoutError("浏览器调试端口未在预期时间内就绪")

    def _cdp_set_cookies(
        self,
        websocket_url: str,
        cookie_records: list[dict[str, Any]],
    ) -> tuple[list[str], list[dict[str, str]]]:
        import websocket

        ws = websocket.create_connection(websocket_url, timeout=5)
        try:
            next_id = 1

            def call(method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
                nonlocal next_id
                message_id = next_id
                next_id += 1
                payload = {"id": message_id, "method": method}
                if params:
                    payload["params"] = params
                ws.send(json.dumps(payload, ensure_ascii=False))
                deadline = time.time() + 8.0
                while time.time() < deadline:
                    raw = ws.recv()
                    response = json.loads(raw)
                    if int(response.get("id") or 0) != message_id:
                        continue
                    if response.get("error"):
                        error = response["error"]
                        raise RuntimeError(str(error.get("message") or error))
                    return response.get("result") or {}
                raise TimeoutError(f"CDP 命令超时：{method}")

            call("Network.enable")
            applied: list[str] = []
            failed: list[dict[str, str]] = []
            for cookie in cookie_records:
                params: dict[str, Any] = {
                    "url": str(cookie.get("url") or ""),
                    "name": str(cookie.get("name") or ""),
                    "value": str(cookie.get("value") or ""),
                }
                if cookie.get("domain"):
                    params["domain"] = str(cookie["domain"])
                if cookie.get("path"):
                    params["path"] = str(cookie["path"])
                if "secure" in cookie:
                    params["secure"] = bool(cookie["secure"])
                if "httpOnly" in cookie:
                    params["httpOnly"] = bool(cookie["httpOnly"])
                if cookie.get("expirationDate"):
                    params["expires"] = float(cookie["expirationDate"])
                same_site = self._normalize_cdp_same_site(cookie.get("sameSite"))
                if same_site is not None:
                    params["sameSite"] = same_site
                try:
                    result = call("Network.setCookie", params)
                    if result.get("success"):
                        applied.append(str(cookie.get("name") or ""))
                    else:
                        failed.append({"name": str(cookie.get("name") or ""), "message": "CDP 返回 success=false"})
                except Exception as exc:
                    failed.append({"name": str(cookie.get("name") or ""), "message": str(exc)})
            return applied, failed
        finally:
            with contextlib.suppress(Exception):
                ws.close()

    def _normalize_cdp_same_site(self, value: Any) -> str | None:
        mapping = {
            "lax": "Lax",
            "strict": "Strict",
            "no_restriction": "None",
            "none": "None",
        }
        if value in (None, "", "unspecified"):
            return None
        normalized = str(value).strip().lower()
        return mapping.get(normalized)

    def _browser_proxy_server(self, proxy_ip: str | None) -> str | None:
        raw = str(proxy_ip or "").strip()
        if not raw:
            return None
        try:
            return self._parse_proxy_endpoint(raw).host_port
        except ValueError:
            return None

    def _sanitize_device_key(self, value: str) -> str:
        cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", str(value or "device")).strip("-")
        return cleaned or "device"
