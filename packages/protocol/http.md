# HTTP Protocol

## 基本规则

- 所有业务 HTTP 接口由 Python runtime 提供。
- 所有成功响应使用统一 envelope：`{ "ok": true, "data": ... }`
- 所有失败响应使用统一 envelope：`{ "ok": false, "error": { ... } }`

## 首批资源域

1. `GET /health`
2. `GET /settings`
3. `GET /accounts`
4. `GET /providers`
5. `GET /tasks`
6. `GET /dashboard/overview`
7. `GET /copywriter/bootstrap`
8. `GET /license/status`
9. `GET /scheduler`

## 鉴权约定

- 除 `GET /health` 外，HTTP 请求统一通过请求头 `X-TKOPS-Token` 传递 runtime token。
- token 由桌面宿主生成并透传给前端与 Python runtime。
- 缺少 token 或 token 不匹配时，返回 `401` 和统一错误 envelope。

## 待补齐

1. 每个资源域的 query/body schema
2. 分页、筛选、排序约定
3. 错误码清单
