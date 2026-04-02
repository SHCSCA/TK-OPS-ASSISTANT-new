# Error Envelope

```json
{
  "ok": false,
  "error": {
    "code": "runtime.unavailable",
    "message": "Runtime is unavailable.",
    "details": {},
    "retryable": true
  }
}
```

## 字段说明

- `code`: 程序可识别错误码
- `message`: 面向用户或日志的可读信息
- `details`: 可选调试或上下文附加信息
- `retryable`: 是否建议前端提供重试入口