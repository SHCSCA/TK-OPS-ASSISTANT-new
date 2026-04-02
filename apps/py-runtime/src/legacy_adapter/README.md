# Legacy Adapter

本目录用于把新 runtime 与旧 `desktop_app` 业务资产隔离开。

规则：

- 新协议层只与本目录或新的 application 层交互。
- 旧 `desktop_app` 模块的直接导入尽量收口到这里。
- 不允许把新的宿主或前端耦合重新写回旧 Bridge。
