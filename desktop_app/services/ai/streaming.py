from __future__ import annotations

"""面向生产场景的 AI 流式运行时。"""

from collections.abc import Mapping, Sequence
from threading import Lock
from typing import Callable, cast
from uuid import uuid4

from ...core.qt import QObject, QThread, Signal
from ...core.runtime.cancellation import CancellationToken
from .provider_adapter import MessagePayload, ProviderAdapter, ResponsePayload


def _coerce_int(value: object) -> int:
    """将任意可解析值转换为非负整数。"""

    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return max(0, value)
    if isinstance(value, float):
        return max(0, int(value))
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return 0
        try:
            return max(0, int(float(text)))
        except ValueError:
            return 0
    return 0


def _empty_usage() -> dict[str, int]:
    """返回标准化的用量结构。"""

    return {
        "total_tokens": 0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
    }


def _string_object_mapping(value: object) -> Mapping[str, object] | None:
    """将任意映射收敛为 string -> object 结构。"""

    if not isinstance(value, Mapping):
        return None

    normalized: dict[str, object] = {}
    raw_mapping = cast(Mapping[object, object], value)
    for raw_key, item in raw_mapping.items():
        if isinstance(raw_key, str):
            key: str = raw_key
            normalized[key] = item
    return normalized


def _normalize_usage(candidate: Mapping[str, object]) -> dict[str, int] | None:
    """从候选映射中抽取标准 token 用量字段。"""

    usage = _empty_usage()
    has_value = False
    for key in usage:
        if key in candidate:
            usage[key] = _coerce_int(candidate[key])
            has_value = True

    if not has_value:
        return None

    if usage["total_tokens"] == 0:
        usage["total_tokens"] = usage["prompt_tokens"] + usage["completion_tokens"]

    return usage


def _extract_usage(payload: Mapping[str, object]) -> dict[str, int] | None:
    """递归扫描响应分块，尽量提取 token 用量。"""

    direct_usage = _normalize_usage(payload)
    if direct_usage is not None:
        return direct_usage

    usage_value = _string_object_mapping(payload.get("usage"))
    if usage_value is not None:
        normalized_usage = _normalize_usage(usage_value)
        if normalized_usage is not None:
            return normalized_usage

    for value in payload.values():
        nested_mapping = _string_object_mapping(value)
        if nested_mapping is not None:
            nested_usage = _extract_usage(nested_mapping)
            if nested_usage is not None:
                return nested_usage
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            for item in value:
                item_mapping = _string_object_mapping(item)
                if item_mapping is not None:
                    nested_usage = _extract_usage(item_mapping)
                    if nested_usage is not None:
                        return nested_usage

    return None


def _copy_payload(chunk: ResponsePayload) -> dict[str, object]:
    """复制 provider 返回的只读载荷，便于跨线程转发。"""

    return dict(chunk)


class _StreamContext:
    """记录单个流式会话的线程与统计信息。"""

    stream_id: str
    thread: QThread
    worker: _StreamingWorker
    cancellation_token: CancellationToken
    model: str
    role_name: str | None
    usage: dict[str, int]

    def __init__(
        self,
        *,
        stream_id: str,
        thread: QThread,
        worker: _StreamingWorker,
        cancellation_token: CancellationToken,
        model: str,
        role_name: str | None,
        usage: dict[str, int],
    ) -> None:
        self.stream_id = stream_id
        self.thread = thread
        self.worker = worker
        self.cancellation_token = cancellation_token
        self.model = model
        self.role_name = role_name
        self.usage = usage


class _StreamingWorker(QObject):
    """在独立线程中执行流式推理并汇报状态。"""

    chunk_received: Signal = Signal(object)
    usage_updated: Signal = Signal(object)
    progress_updated: Signal = Signal(int)
    completed: Signal = Signal()
    failed: Signal = Signal(str)

    def __init__(
        self,
        adapter: ProviderAdapter,
        model: str,
        messages: Sequence[MessagePayload],
        temperature: float,
        cancellation_token: CancellationToken,
    ) -> None:
        super().__init__()
        self._adapter: ProviderAdapter = adapter
        self._model: str = model
        self._messages: list[MessagePayload] = list(messages)
        self._temperature: float = temperature
        self._cancellation_token: CancellationToken = cancellation_token
        self._usage_snapshot: dict[str, int] = _empty_usage()
        self._chunk_count: int = 0

    def _merge_usage(self, chunk_usage: dict[str, int]) -> None:
        """使用幂等方式合并分块中携带的累计用量。"""

        for key, value in chunk_usage.items():
            if key not in self._usage_snapshot:
                continue
            self._usage_snapshot[key] = max(self._usage_snapshot[key], value)

        if self._usage_snapshot["total_tokens"] == 0:
            self._usage_snapshot["total_tokens"] = (
                self._usage_snapshot["prompt_tokens"] + self._usage_snapshot["completion_tokens"]
            )

    def _emit_usage(self) -> None:
        """向上游发送当前累计用量快照。"""

        self.usage_updated.emit(dict(self._usage_snapshot))

    def _emit_progress(self) -> None:
        """基于已接收分块数量输出近似进度。"""

        progress = min(99, 5 + self._chunk_count * 5)
        self.progress_updated.emit(progress)

    def run(self) -> None:
        """执行 provider 流式调用，并在取消或异常时优雅收尾。"""

        self.progress_updated.emit(0)
        self._emit_usage()

        try:
            if self._cancellation_token.is_cancelled:
                self.progress_updated.emit(100)
                self.completed.emit()
                return

            for chunk in self._adapter.stream(
                model=self._model,
                messages=self._messages,
                temperature=self._temperature,
            ):
                if self._cancellation_token.is_cancelled:
                    break

                payload = _copy_payload(chunk)
                chunk_usage = _extract_usage(payload)
                if chunk_usage is not None:
                    self._merge_usage(chunk_usage)
                    self._emit_usage()

                self._chunk_count += 1
                self.chunk_received.emit(payload)
                self._emit_progress()

                if self._cancellation_token.is_cancelled:
                    break

            self.progress_updated.emit(100)
            self._emit_usage()
            self.completed.emit()
        except Exception as exc:  # pragma: no cover - 运行时兜底
            self.progress_updated.emit(100)
            self._emit_usage()
            self.failed.emit(str(exc) or exc.__class__.__name__)


class StreamingAIRuntime(QObject):
    """管理 AI 流式线程生命周期、取消状态与用量统计。"""

    chunk_received: Signal = Signal(object)
    stream_started: Signal = Signal(str)
    stream_completed: Signal = Signal()
    stream_failed: Signal = Signal(str)
    usage_updated: Signal = Signal(object)
    progress_updated: Signal = Signal(int)

    service_name: str = "ai_runtime"

    def __init__(self) -> None:
        super().__init__()
        self._lock: Lock = Lock()
        self._initialized: bool = False
        self._streams: dict[str, _StreamContext] = {}
        self._current_stream_id: str | None = None
        self._usage_totals: dict[str, int] = _empty_usage()

    def initialize(self) -> None:
        """初始化运行时内部状态。"""

        with self._lock:
            if self._initialized:
                return
            self._initialized = True

    def shutdown(self) -> None:
        """取消所有活跃流并等待线程尽量完成清理。"""

        self.initialize()

        with self._lock:
            contexts = list(self._streams.values())
            self._current_stream_id = None

        for context in contexts:
            context.cancellation_token.cancel()
            context.thread.quit()

        for context in contexts:
            if context.thread.wait(1000):
                self._clear_runtime_state(context.stream_id)

    def healthcheck(self) -> dict[str, object]:
        """返回流式服务当前健康状态与活跃流数量。"""

        with self._lock:
            current_stream_id = self._current_stream_id
            active_stream_count = len(self._streams)
            current_context = self._streams.get(current_stream_id) if current_stream_id is not None else None

        return {
            "service": self.service_name,
            "status": "ok" if self._initialized else "not_initialized",
            "active_stream_count": active_stream_count,
            "is_streaming": current_stream_id is not None,
            "current_model": current_context.model if current_context is not None else None,
            "current_role_name": current_context.role_name if current_context is not None else None,
        }

    def start_stream(
        self,
        *,
        adapter: ProviderAdapter,
        model: str,
        messages: Sequence[MessagePayload],
        temperature: float = 0.0,
        role_name: str | None = None,
        cancellation_token: CancellationToken | None = None,
    ) -> None:
        """创建流式 worker 并启动一次新的推理会话。"""

        self.initialize()
        self.cancel_current_stream()

        stream_id = uuid4().hex
        thread = QThread()
        token = cancellation_token or CancellationToken()
        worker = _StreamingWorker(
            adapter=adapter,
            model=model,
            messages=messages,
            temperature=temperature,
            cancellation_token=token,
        )
        worker.moveToThread(thread)

        context = _StreamContext(
            stream_id=stream_id,
            thread=thread,
            worker=worker,
            cancellation_token=token,
            model=model,
            role_name=role_name,
            usage=_empty_usage(),
        )

        worker.chunk_received.connect(self.chunk_received.emit)
        worker.usage_updated.connect(self._make_usage_callback(stream_id))
        worker.progress_updated.connect(self.progress_updated.emit)
        worker.completed.connect(self._make_completed_callback(stream_id))
        worker.failed.connect(self._make_failed_callback(stream_id))
        worker.completed.connect(thread.quit)
        worker.failed.connect(thread.quit)
        thread.started.connect(worker.run)
        thread.finished.connect(self._make_cleanup_callback(stream_id))

        with self._lock:
            self._streams[stream_id] = context
            self._current_stream_id = stream_id

        self.progress_updated.emit(0)
        self.usage_updated.emit(
            {
                "stream_id": stream_id,
                "model": model,
                "role_name": role_name,
                "usage": dict(context.usage),
                "totals": self.get_usage_stats(),
            }
        )
        self.stream_started.emit(model)
        thread.start()

    def cancel_current_stream(self) -> None:
        """取消当前流并请求其线程尽快退出。"""

        with self._lock:
            stream_id = self._current_stream_id
            context = self._streams.get(stream_id) if stream_id is not None else None
            self._current_stream_id = None

        if context is None:
            return

        context.cancellation_token.cancel()
        context.thread.quit()
        _ = context.thread.wait(1000)

    def is_streaming(self) -> bool:
        """返回当前是否存在可取消的活跃流。"""

        with self._lock:
            return self._current_stream_id is not None

    def get_usage_stats(self) -> dict[str, int]:
        """返回运行时累计 token 用量。"""

        with self._lock:
            return dict(self._usage_totals)

    def _handle_stream_completed(self, stream_id: str) -> None:
        """在流完成时汇总用量并向上游广播完成事件。"""

        self._finalize_usage(stream_id)
        self.progress_updated.emit(100)
        self.stream_completed.emit()

    def _handle_stream_failed(self, stream_id: str, error: str) -> None:
        """在流失败时汇总用量并向上游广播错误。"""

        self._finalize_usage(stream_id)
        self.progress_updated.emit(100)
        self.stream_failed.emit(error)

    def _finalize_usage(self, stream_id: str) -> None:
        """将单流用量累加到运行时总量，且保证只记账一次。"""

        with self._lock:
            context = self._streams.get(stream_id)
            if context is None:
                return

            for key, value in context.usage.items():
                self._usage_totals[key] += value

            usage_payload = {
                "stream_id": stream_id,
                "model": context.model,
                "role_name": context.role_name,
                "usage": dict(context.usage),
                "totals": dict(self._usage_totals),
            }
            context.usage = _empty_usage()

        self.usage_updated.emit(usage_payload)

    def _handle_usage_updated(self, stream_id: str, usage: object) -> None:
        """更新单流用量快照并广播当前状态。"""

        usage_mapping = _string_object_mapping(usage)
        if usage_mapping is None:
            return

        normalized_usage = _normalize_usage(usage_mapping)
        if normalized_usage is None:
            return

        with self._lock:
            context = self._streams.get(stream_id)
            if context is None:
                return

            for key, value in normalized_usage.items():
                context.usage[key] = max(context.usage[key], value)

            if context.usage["total_tokens"] == 0:
                context.usage["total_tokens"] = (
                    context.usage["prompt_tokens"] + context.usage["completion_tokens"]
                )

            usage_payload = {
                "stream_id": stream_id,
                "model": context.model,
                "role_name": context.role_name,
                "usage": dict(context.usage),
                "totals": dict(self._usage_totals),
            }

        self.usage_updated.emit(usage_payload)

    def _make_usage_callback(self, stream_id: str) -> Callable[[object], None]:
        """生成绑定到指定流的用量更新回调。"""

        def callback(usage: object) -> None:
            self._handle_usage_updated(stream_id, usage)

        return callback

    def _make_completed_callback(self, stream_id: str) -> Callable[[], None]:
        """生成绑定到指定流的完成回调。"""

        def callback() -> None:
            self._handle_stream_completed(stream_id)

        return callback

    def _make_failed_callback(self, stream_id: str) -> Callable[[str], None]:
        """生成绑定到指定流的失败回调。"""

        def callback(error: str) -> None:
            self._handle_stream_failed(stream_id, error)

        return callback

    def _make_cleanup_callback(self, stream_id: str) -> Callable[[], None]:
        """生成绑定到指定流的线程清理回调。"""

        def callback() -> None:
            self._clear_runtime_state(stream_id)

        return callback

    def _clear_runtime_state(self, stream_id: str) -> None:
        """在线程结束后移除引用，避免悬挂线程对象残留。"""

        with self._lock:
            context = self._streams.pop(stream_id, None)
            if self._current_stream_id == stream_id:
                self._current_stream_id = None

        if context is None:
            return

        delete_worker = getattr(context.worker, "deleteLater", None)
        if callable(delete_worker):
            _ = delete_worker()

        delete_thread = getattr(context.thread, "deleteLater", None)
        if callable(delete_thread):
            _ = delete_thread()
