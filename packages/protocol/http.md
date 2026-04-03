# HTTP Protocol

## 基本规则

- 所有业务 HTTP 接口由 Python runtime 提供。
- 所有成功响应使用统一 envelope：`{ "ok": true, "data": ... }`
- 所有失败响应使用统一 envelope：`{ "ok": false, "error": { ... } }`

## 运行入口（当前默认）

- 默认本地入口：`http://127.0.0.1:<runtime-port>`
- 开发链路：`apps/desktop` 通过该入口访问 `apps/py-runtime`
- 旧 `desktop_app` 不再作为默认运行入口，仅保留迁移参考定位。

## 首批资源域

1. `GET /health`
2. `GET /settings`
3. `GET /accounts`
4. `GET /accounts/{account_id}`
5. `GET /accounts/{account_id}/activity`
6. `GET /providers`
7. `GET /tasks`
8. `GET /dashboard/overview`
9. `GET /copywriter/bootstrap`
10. `GET /license/status`
11. `GET /scheduler`

## 鉴权约定

- 除 `GET /health` 外，HTTP 请求统一通过请求头 `X-TKOPS-Token` 传递 runtime token。
- token 由桌面宿主生成并透传给前端与 Python runtime。
- 缺少 token 或 token 不匹配时，返回 `401` 和统一错误 envelope。

## `GET /health` 协议元信息约定

`/health` 除返回可探活状态外，还提供最小协议边界元信息：

```json
{
  "ok": true,
  "data": {
    "status": "ok",
    "version": "1.3.0",
    "protocol": {
      "version": "2026-04-01",
      "auth": {
        "header": "X-TKOPS-Token",
        "wsQuery": "token"
      }
    }
  }
}
```

说明：

- `protocol.version`：HTTP/WS 当前统一协议版本标识。
- `protocol.auth.header`：HTTP 令牌请求头名称。
- `protocol.auth.wsQuery`：WS 查询参数令牌字段名称。
- 桌面宿主与前端可据此进行最小自检，避免 hardcode 漂移。

## 待补齐

1. 每个资源域的 query/body schema
2. 分页、筛选、排序约定
3. 错误码清单
