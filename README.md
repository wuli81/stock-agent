# stock-agent

A 股自动化交易 Agent 系统（v0.1 骨架）

> ⚠️ 仅供学习研究，不构成投资建议；实盘使用请自行评估风险并遵守当地法律法规。

## 项目结构

```
stock-agent/
├── backend/          # Linux 策略服务器（FastAPI + SQLAlchemy + Alembic）
│   ├── app/
│   │   ├── api/          # REST 路由
│   │   ├── core/         # 配置、安全、日志
│   │   ├── data/         # 数据获取（akshare，可替换）
│   │   ├── strategy/     # 策略引擎 + plugins/ 示例策略
│   │   ├── planner/      # 交易计划生成
│   │   ├── scheduler/    # 定时任务（15:30 收盘分析）
│   │   ├── repository/   # 数据访问
│   │   └── models/       # ORM 模型
│   ├── migrations/       # Alembic 迁移
│   ├── tests/
│   ├── Dockerfile
│   └── docker-compose.yml
├── trade-executor/   # Windows 执行器
│   ├── executor/
│   │   ├── receiver/     # 拉取计划
│   │   ├── trader/       # 下单引擎 + adapters/（Demo / Paper / Client）
│   │   ├── ocr/          # 屏幕识别（占位）
│   │   ├── ui/           # PySide6 桌面界面 + 控制台
│   │   └── logger/       # 本地日志
│   └── tests/
├── shared/           # 共享层：数据结构 / 枚举 / 常量
├── docs/             # 设计文档（PRD / 架构 / 数据库 / REST API / OpenAPI）
└── examples/         # 示例
```

## 快速开始

### 后端

```bash
# 1) 创建虚拟环境（Python 3.11+）
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
# source .venv/bin/activate

# 2) 安装
pip install -e ./shared
pip install -e "./backend[dev]"

# 3) 初始化数据库并启动
cd backend
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

- 交互文档：http://localhost:8000/docs
- 默认 API Key：`dev-key`（可在 `backend/.env` 中修改）

### 运行后端测试

```bash
cd backend
pytest
```

### 执行器（Windows，Demo 模式）

```bash
pip install -e "./trade-executor[dev]"
cd trade-executor
cp config.toml.example config.toml
python -m executor.main --config config.toml --date 2026-08-08
```

### Docker 部署后端

```bash
cd backend
docker compose up --build
```
> **验证状态**：当前开发机未安装 Docker，已用「容器运行时模拟」验证等价路径：
> 干净 venv 中非 editable 安装 shared + backend → 绝对路径数据库上 `alembic upgrade head` →
> uvicorn 启动后 `/health` 返回 200、鉴权接口正常、无鉴权请求被 401 拒绝。
> 在安装 Docker 的机器上执行 `docker compose up --build` 即可完成真实构建与部署。


## 数据获取与收盘分析

依赖 akshare（需联网访问行情数据源；当前沙箱环境无法访问外网行情接口）：

```bash
pip install -e "./backend[data]"
cd backend

# 1) 拉取全部 A 股基础信息入库
python -m app.cli seed-basics

# 2) 拉取跟踪股票日线（建议先在 .env 配置 STOCK_AGENT_TRACKED_STOCKS）
python -m app.cli fetch-daily --codes 600000,000001 --days 60

# 3) 手动运行一次收盘分析（数据 -> 策略 -> 计划 -> 每日报告）
python -m app.cli run-analysis --date 2026-08-07
```

设置 `STOCK_AGENT_ENABLE_SCHEDULER=true` 后，每个交易日 15:30 由 APScheduler 自动执行
`backend/app/scheduler/jobs.py` 的 `run_daily_analysis`，完成：拉取行情 -> 运行策略 -> 生成计划 ->
落库 -> 生成每日报告。


## API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/health | 健康检查 |
| GET | /api/v1/trade-plans?date= | 查询交易计划 |
| GET | /api/v1/trade-plans/{id} | 计划详情 |
| POST | /api/v1/trades | 上报成交（幂等） |
| GET | /api/v1/trades | 查询成交 |
| GET | /api/v1/account | 账户快照 |
| GET | /api/v1/daily-reports/{date} | 每日报告 |
| GET | /api/v1/strategies | 策略列表 |
| POST | /api/v1/executor/heartbeat | 执行器心跳 |

完整规范见 `docs/openapi.yaml` 与 `docs/REST-API-设计文档.md`。

## v0.2：桌面界面与券商适配

```bash
# 安装 GUI 依赖（可选）
pip install -e "./trade-executor[gui]"

# 启动桌面界面
cd trade-executor
python -m executor.main --gui
# 或直接
python -m executor.ui.app
```

券商适配器通过 `config.toml` 的 `broker` 选择：

| broker | 说明 |
|--------|------|
| `paper`（默认） | 纸面撮合：价格区间校验、风控拒单、部分成交，可用于测试与回测 |
| `demo` | 简单模拟成交 |
| `client` | pywinauto 真实客户端自动化脚手架（实验性，默认 dry-run 防误操作） |

下单引擎：计划项 → 限价单（取价格区间中间价）→ 适配器撮合 → 失败自动重试。

## CI（GitHub Actions）

推送 / PR 到 `main`、`master` 时自动执行（配置见 `.github/workflows/ci.yml`）：

- Python 3.11 / 3.12 矩阵；
- `ruff check .` 静态检查；
- backend 与 trade-executor 的 pytest 测试；
- 全新数据库上执行 `alembic upgrade head` + `alembic check`（验证迁移与 ORM 模型一致）。

推送到 GitHub 后即可在仓库的 **Actions** 页面查看结果。

## 文档

| 文档 | 说明 |
|------|------|
| docs/PRD-需求文档.md | 需求文档 |
| docs/系统架构设计文档.md | 架构、模块接口、时序图 |
| docs/数据库设计文档.md | 表结构与 DDL |
| docs/REST-API-设计文档.md | REST API 设计 |
| docs/openapi.yaml | OpenAPI 3.0.3 规范 |

## v0.1 范围

- [x] 项目骨架（backend / trade-executor / shared）
- [x] 数据库 ORM 模型 + Alembic 迁移
- [x] REST API（计划 / 成交 / 账户 / 报告 / 策略 / 心跳）
- [x] 示例策略（ma_cross）+ 计划生成
- [x] 执行器 Demo 适配器（模拟下单）+ 失败重试
- [x] 真实行情数据获取（akshare）+ 收盘调度闭环（数据 -> 策略 -> 计划 -> 报告）
- [ ] 真实券商 GUI 自动化 / OCR
- [x] GitHub Actions CI（lint + 测试 + 迁移校验）
- [x] Docker 部署验证（运行时路径模拟验证；真实镜像构建需 Docker 环境）


## v0.3：OCR 成交确认

```bash
# 安装 OCR 依赖（二选一；Tesseract 还需在系统安装 Tesseract 引擎）
pip install pytesseract      # 或 pip install paddleocr

# 试识别：截取券商界面区域并解析成交结果
cd trade-executor
python -m executor.main --ocr-check --region 100,200,400,120
```

- 引擎：`ocr_engine = "tesseract" | "paddle" | "fake"`（config.toml）；
- 解析器：OCR 文本 → 成交状态（全部成交 / 部分成交 / 废单 / 未成交）+ 数量 + 价格；
- `client` 适配器 dry-run 模式可结合 OCR 读取交易软件当前界面状态（默认不点击、不下单）。

## v0.2 范围

- [x] 券商适配器框架：Demo / Paper（模拟撮合）/ Client（pywinauto 脚手架）
- [x] 限价单（价格区间中间价）+ 区间校验 + 风控拒单 + 部分成交
- [x] PySide6 桌面界面（计划表格 / 拉取 / 执行 / 停止 / 日志）
- [ ] 真实券商客户端控件自动化（需在装有券商客户端的机器上验证控件定位）
- [ ] OCR 成交确认（PaddleOCR / Tesseract）


## v0.3 范围

- [x] OCR 成交确认子系统：Tesseract / PaddleOCR / Fake 引擎 + 成交文本解析
- [x] 屏幕区域截图 + `--ocr-check` 试识别 CLI
- [x] `client` 适配器 dry-run 集成 OCR 状态读取
- [ ] 真实券商控件自动化（pywinauto 控件定位，需真实环境校准）
- [ ] 订单 / 成交状态与后端 orders 表同步
