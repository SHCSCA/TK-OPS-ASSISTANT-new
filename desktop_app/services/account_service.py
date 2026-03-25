"""Account & Group management service."""
from __future__ import annotations

import datetime as _dt
import json
import re
import socket

from typing import Any, Sequence

import httpx

from desktop_app.database.models import Account, Asset, Device, Group, Task
from desktop_app.database.repository import Repository


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


class AccountService:
    def __init__(self, repo: Repository | None = None) -> None:
        self._repo = repo or Repository()

    def create_account(self, username: str, **kwargs: Any) -> Account:
        return self._repo.add(Account(username=username, **kwargs))

    def list_accounts(self, *, status: str | None = None) -> Sequence[Account]:
        return self._repo.list_accounts(status=status)

    def get_account(self, pk: int) -> Account | None:
        return self._repo.get_by_id(Account, pk)

    def update_account(self, pk: int, **fields: Any) -> Account | None:
        account = self._repo.get_by_id(Account, pk)
        if account is None:
            return None
        return self._repo.update(account, **fields)

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
            identity = self._extract_tiktok_identity(payload)
            if identity:
                return {
                    "status": "valid",
                    "label": "已登录",
                    "message": f"已通过 TikTok 账号接口确认登录态，可识别账号 {identity}",
                    "target": str(response.request.url),
                    "http_status": response.status_code,
                }
            if response.status_code in {401, 403} or self._payload_indicates_invalid_login(payload):
                detail = self._extract_error_message(payload) or f"HTTP {response.status_code}"
                return {
                    "status": "invalid",
                    "label": "未登录",
                    "message": f"TikTok 返回未登录或已失效：{detail}",
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
        data = payload.get("data") if isinstance(payload, dict) else None
        candidates = [payload, data] if isinstance(data, dict) else [payload]
        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue
            for key in ("username", "unique_id", "screen_name", "nickname", "user_id", "uid"):
                value = candidate.get(key)
                if value:
                    return str(value)
            for nested_key in ("user", "account_info", "account", "user_info"):
                nested = candidate.get(nested_key)
                if isinstance(nested, dict):
                    for key in ("username", "unique_id", "screen_name", "nickname", "user_id", "uid"):
                        value = nested.get(key)
                        if value:
                            return str(value)
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
        message = self._extract_error_message(payload).lower()
        if not message:
            return False
        invalid_markers = (
            "login",
            "not login",
            "not logged",
            "expired",
            "invalid",
            "unauthorized",
            "challenge_required",
            "checkpoint_required",
            "请登录",
            "登录",
            "失效",
        )
        return any(marker in message for marker in invalid_markers)

    def _extract_error_message(self, payload: dict[str, Any]) -> str:
        for mapping in self._iter_payload_mappings(payload):
            for key in ("message", "status_msg", "error_message", "description", "detail"):
                value = mapping.get(key)
                if value:
                    return str(value)
        return ""

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
        self._repo.delete(device)
        return True

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
