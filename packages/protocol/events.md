# WebSocket Events

## 基本规则

- WebSocket 只承载长任务与实时事件。
- 所有事件必须有显式 `type` 字段。
- 前端统一通过事件路由器消费，不允许页面私有裸连协议。

## 首批事件

1. `runtime.handshake`
2. `runtime.status`
3. `ai.stream.delta`
4. `ai.stream.done`
5. `ai.stream.error`

## 握手与 token 约定

- WebSocket 连接支持以下 token 透传方式（优先 query）：
  1. 查询参数：`?token=<runtime-token>`
  2. 请求头：`X-TKOPS-Token: <runtime-token>`
- token 校验失败时，runtime 直接拒绝连接，关闭码为 `4401`。
- 连接建立并鉴权通过后，runtime 首先发送 `runtime.handshake`，再进入业务事件流。
- `runtime.status` 用作最轻量就绪事件，确认 runtime 已就绪并返回版本信息。

## `runtime.handshake` 载荷约定

```json
{
  "type": "runtime.handshake",
  "payload": {
    "channel": "runtime-status",
    "protocolVersion": "2026-04-01",
    "appVersion": "1.3.0",
    "auth": {
      "scheme": "session_token"
    }
  }
}
```

字段说明：

- `payload.channel`：当前 WS 通道标识（例如 `runtime-status`、`copywriter-stream`）。
- `payload.protocolVersion`：WS 协议版本，用于客户端能力判断。
- `payload.appVersion`：runtime 版本号，便于宿主与客户端对齐诊断。
- `payload.auth.scheme`：当前鉴权方案标识。

## 待补齐

1. `task.progress` / `task.completed` / `task.failed` 事件正式接入
2. 重连策略
3. 错误事件负载结构
