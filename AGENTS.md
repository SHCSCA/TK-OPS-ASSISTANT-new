# TK-OPS ASSISTANT

## Project Overview

TK-OPS 是一个面向 TikTok Shop 运营的企业级 Windows 桌面应用，提供全链路的选品、文案、二创、运营自动化能力。

## Tech Stack

- **桌面框架**: PySide6 (Qt for Python)
- **后端**: Python 3.11+
- **AI 集成**: OpenAI API (GPT-4o)
- **数据库**: SQLite + SQLAlchemy
- **架构**: Clean Architecture / MVVM

## Directory Structure

```
TK-OPS-ASSISTANT-new/
├── desktop_app/                 # 主应用代码
│   ├── main.py                 # GUI MVP 入口 (PySide6)
│   ├── cli_mvp.py              # CLI MVP 入口 (无 GUI)
│   ├── models.py               # 数据模型 (dataclass)
│   ├── db.py                   # SQLite/SQLAlchemy 数据库
│   ├── requirements.txt        # Python 依赖
│   ├── core/                   # 核心工具
│   │   ├── config.py           # 配置加载
│   │   └── logger.py           # 日志工具
│   ├── ai/                     # AI 集成
│   │   └── openai_client.py    # OpenAI API 封装
│   ├── tiktok/                 # TikTok API 集成
│   │   └── api_client.py      # TikTok Shop API 封装
│   ├── pipeline/               # 业务管线
│   │   └── pipeline.py        # 全链路 Pipeline
│   └── ui/                     # UI 组件
│       └── main_window.py     # 主窗口骨架
├── stitch_text_document/       # 设计稿 (HTML/Tailwind)
│   ├── ANALYSIS.md            # 设计稿分析报告
│   └── [多个子目录]           # 各模块的设计稿
└── venv/                      # Python 虚拟环境
```

## Key Modules

### desktop_app/main.py
- **入口**: Windows GUI 应用
- **功能**: 选品、文案生成、运营自动化三大模块
- **UI**: PySide6，三列布局 (导航/主区域/日志)

### desktop_app/cli_mvp.py
- **入口**: 无 GUI 的 CLI 版本
- **功能**: 演示选品、文案生成、运营流程
- **用途**: 快速验证核心逻辑

### desktop_app/ai/openai_client.py
- **功能**: 封装 OpenAI ChatCompletion API
- **模型**: GPT-4o (默认)
- **特性**: 支持 API Key 环境变量注入，离线回退

### desktop_app/pipeline/pipeline.py
- **功能**: 选品 → 文案生成 → 投放计划的端到端管线**: 演示自动化工作流

## Development Status

- [
- **用途x] MVP 骨架代码
- [x] PySide6 GUI 原型
- [x] CLI MVP 版本
- [x] OpenAI 集成
- [ ] TikTok Shop API 真实对接
- [ ] 本地数据持久化
- [ ] 打包发布

## How to Run

### GUI 版本
```bash
# 激活虚拟环境
cd desktop_app
..\venv\Scripts\activate

# 设置 OpenAI API Key (可选)
set OPENAI_API_KEY=sk-...

# 启动
python main.py
```

### CLI 版本
```bash
cd desktop_app
python cli_mvp.py
```

## Notes for AI Agents

- Python 版本: 3.8+ (推荐 3.11+)
- 依赖管理: pip + requirements.txt
- 主要入口: `desktop_app/main.py` (GUI) / `desktop_app/cli_mvp.py` (CLI)
- 测试框架: pytest (待集成)
