# Data Engineering Week 1: Minimal Data Pipeline

## 🚀 项目概述
本项目是数据工程学习的第一周任务：建立工程脚手架并实现一个从 World Bank 拉取数据到本地 Parquet 的最小化数据管道。

## 🛠 技术栈
- **包管理**: [uv](https://github.com/astral-sh/uv) (替代 poetry，更快的 Python 包管理工具)
- **代码规范**: [Ruff](https://github.com/astral-sh/ruff) (Linting & Formatting)
- **日志**: [Loguru](https://github.com/Delgan/loguru) (支持 JSON 序列化)
- **数据库**: SQLite + SQLAlchemy (记录元数据)
- **数据处理**: Pandas + PyArrow (Parquet 存储)
- **测试**: Pytest

## 📁 目录结构
```text
.
├── app/
│   ├── tools/          # CLI 工具
│   │   └── data_ingest.py
│   └── utils/          # 通用工具（日志、数据库）
│       ├── logger.py
│       └── metadata_db.py
├── data/
│   └── raw/            # 存储落盘的 Parquet 文件
├── logs/               # JSON 格式日志
├── tests/              # 单元测试
├── .env.example        # 环境变量模板
├── pyproject.toml      # uv 配置文件
└── metadata.db         # SQLite 元数据数据库
```

## ⚙️ 安装与运行指南

### 1. 安装 uv
如果你还没有安装 uv，请参考 [uv 官方文档](https://github.com/astral-sh/uv)。

### 2. 初始化环境
```bash
uv sync
```

### 3. 运行数据拉取
使用以下命令从 World Bank 拉取中国和美国的 GDP 增长率数据：
```bash
export PYTHONPATH=$PYTHONPATH:.
uv run python -m app.tools.data_ingest \
    --source worldbank \
    --indicator NY.GDP.MKTP.KD.ZG \
    --countries CN,US \
    --start 2010 \
    --end 2024
```

### 4. 运行测试
```bash
uv run pytest tests/test_ingest.py
```

## 📊 验收标准达成情况
- [x] **工程脚手架**: 使用 uv 初始化，配置了 ruff 和 pre-commit。
- [x] **数据拉取**: 支持 World Bank API，参数化查询。
- [x] **存储**: 数据保存为 Parquet，元数据记录在 SQLite 中。
- [x] **日志**: 实现 trace_id 追踪，支持 JSON 格式输出。
- [x] **测试**: 通过 3 个单元测试，验证了字段、行数及基本幂等性。

## 💡 学习笔记
1. **为什么选择 uv?** uv 是目前 Python 社区最快的包管理工具，集成了 pip, venv, poetry 的功能。
2. **元数据的重要性**: 在生产环境中，我们需要追踪数据的来源、抓取时间和版本，以便在数据出现问题时进行回溯。
3. **结构化日志**: 使用 JSON 格式日志可以方便地被 ELK 或 Grafana 等工具解析。
