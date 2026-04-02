# desktop_app 目录说明

本目录已经降级为迁移参考代码区。

允许用途：

- 复用数据库模型、迁移、服务层与样本数据
- 对照旧页面行为与运行时链路
- 为新 runtime 编写 adapter

禁止用途：

- 继续新增页面逻辑
- 继续新增 Bridge 业务 slot
- 继续作为默认联调入口
- 继续作为未来发布宿主

当前唯一继续演进的目标结构为：

- `apps/desktop`
- `apps/py-runtime`
