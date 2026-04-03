# Runtime 协议边界迁移说明（2026-04-02）

## 1. 目的

本说明用于收口 TK-OPS 新链路中的 runtime 协议边界，确保：

1. `apps/desktop` 与 `apps/py-runtime` 采用一致鉴权语义。
2. HTTP 与 WS 在“入口、握手、错误反馈”上口径一致。
3. 旧 `desktop_app` 不再作为默认运行入口，仅保留迁移参考。

---

## 2. 默认运行入口

- 默认开发入口：`scripts/dev.ps1`
- 默认运行链路：`apps/desktop`（宿主） + `apps/py-runtime`（业务 runtime）
- 旧链路定位：`desktop_app/` 仅用于迁移参考与历史资产复用

---

## 3. 鉴权边界（session_token）

## 3.1 HTTP

- 除 `GET /health` 外，统一使用请求头：
  - `X-TKOPS-Token: <runtime-token>`
- token 无效时返回 `401` + 统一错误 envelope。

## 3.2 WebSocket

- 支持两种透传方式（优先 query）：
  1. `?token=<runtime-token>`
  2. `X-TKOPS-Token: <runtime-token>`
- token 无效时关闭连接：
  - close code：`4401`
  - reason：`invalid runtime token`

---

## 4. 握手边界（WebSocket）

连接建立并鉴权通过后，服务端必须先发 `runtime.handshake`，再进入业务事件流。

示例：

```json
{
  "type": "runtime.handshake",
  "payload": {
    "channel": "runtime-status",
    "protocolVersion": "2026-04-01",
    "appVersion": "1.3.0",
    "auth": { "scheme": "session_token" }
  }
}
```

当前已接入握手的通道：

- `/ws/runtime-status`
- `/ws/copywriter-stream`

---

## 5. `/health` 边界

`GET /health` 除可探活字段外，需返回最小协议元信息：

- `protocol.version`
- `protocol.auth.header`
- `protocol.auth.wsQuery`

该信息用于桌面宿主与前端进行连接参数自检，降低协议字段硬编码风险。

---

## 6. 迁移完成判定（本主题）

以下条件全部满足，判定“runtime 协议边界收口完成”：

1. HTTP/WS 鉴权均复用同一套 token 语义。
2. `/health` 返回协议元信息并已文档化。
3. WS 握手事件在核心通道已稳定发出。
4. 协议文档（`packages/protocol/http.md` / `events.md`）与实现一致。
5. 相关自动化测试覆盖新握手与 health 协议字段。
