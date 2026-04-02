# WebSocket Events

## 基本规则

- WebSocket 只承载长任务与实时事件。
- 所有事件必须有显式 `type` 字段。
- 前端统一通过事件路由器消费，不允许页面私有裸连协议。

## 首批事件

1. `runtime.status`
2. `ai.stream.delta`
3. `ai.stream.done`
4. `ai.stream.error`

## 握手与 token 约定

- WebSocket 连接统一通过查询参数 `?token=<runtime-token>` 透传 token。
- token 校验失败时，runtime 直接拒绝连接，关闭码为 `4401`。
- `runtime.status` 用作最轻量的握手确认事件，确认 runtime 已就绪并返回版本信息。

## 待补齐

1. `task.progress` / `task.completed` / `task.failed` 事件正式接入
2. 重连策略
3. 错误事件负载结构
