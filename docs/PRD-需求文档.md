# stock-agent 项目需求文档（PRD）

> 版本：v0.1（草稿）　|　更新日期：2026-08-07　|　状态：待评审
> 文档来源：ChatGPT 共享对话《国内AI Agent 控制软件》延续

---

## 1. 项目概述

### 1.1 项目名称
stock-agent —— A 股自动化交易 Agent 系统

### 1.2 一句话描述
每个交易日收盘后自动获取行情数据、按策略生成交易计划；次日开盘后由 Windows 端自动完成下单，并自动记录所有交易日志与每日报告。

### 1.3 项目目标（v1.0）
- 每天收盘后自动完成 A 股数据分析与选股；
- 自动生成可执行的 `trade_plan.json`（含标的、方向、数量、价格区间、风控条件）；
- Windows 执行器自动启动交易软件并完成下单；
- 自动记录订单、成交、盈亏与运行日志；
- 生成每日交易报告。

### 1.4 非目标（v1.0 不做）
- 不做 AI 风控 / 新闻分析 / 自动参数优化（v1.0 之后迭代）；
- 不接入融资融券、期权、期货；
- 不做多券商同时下单（先支持单一券商）。

---

## 2. 背景与动机

- 用户希望把「每日选股 + 自动下单 + 交易记录」做成一个可长期维护的开源 GitHub 项目，而非零散脚本。
- 系统跨 Linux（策略/后端）与 Windows（交易客户端/GUI）两端，需要明确的通信协议与模块边界。
- 使用多 Agent（Codex 主开发，Claude Code / Gemini CLI / Cursor 辅助）协作开发，要求代码可测试、可部署、可交接。

---

## 3. 用户与使用场景

| 角色 | 使用场景 |
|------|---------|
| 策略开发者 | 编写/调试选股策略，回测，调整参数 |
| 系统管理员 | 部署 Linux 后端、配置数据库与定时任务 |
| 交易使用者 | 在 Windows 端查看交易计划、启动/暂停自动执行、查看日志 |
| 维护者 | 阅读文档、运行测试、构建 Docker 镜像、发布新版本 |

典型流程：
1. 收盘后（如 15:30）后端定时任务拉取当日行情 → 运行策略 → 生成 `trade_plan.json` 并入库；
2. Windows 执行器（次日开盘前）拉取交易计划 → 等待开盘 → 启动交易软件 → 按计划下单；
3. 执行器回传成交结果 → 后端记录订单与成交 → 生成每日报告。

---

## 4. 总体架构

```
stock-agent/
├── backend/          # Linux 策略服务器（Python）
│   ├── data/         # 获取 A 股数据（行情、财务）
│   ├── strategy/     # 选股策略
│   ├── planner/      # 交易计划生成
│   ├── api/          # REST API
│   └── database/     # 数据访问层
├── trade-executor/   # Windows 执行器
│   ├── receiver/     # 拉取交易计划
│   ├── trader/       # 下单执行
│   ├── ui/           # 桌面界面（状态/日志/手动确认）
│   ├── ocr/          # 屏幕识别（可选，用于 GUI 下单确认）
│   └── logger/       # 本地日志与回传
├── shared/           # 两端共享：通信协议、数据结构、枚举
├── docs/             # 文档
├── examples/         # 示例配置与脚本
└── README.md
```

架构原则：
- 后端与执行器通过 `shared/` 中定义的数据结构/协议解耦；
- 执行器不依赖具体券商实现，通过适配层隔离；
- 所有关键路径可测试、可 mock。

---

## 5. 功能需求

### 5.1 行情数据获取（backend/data）
- FR-01：支持日线行情获取（收盘后自动拉取）；
- FR-02：支持股票基础信息（代码、名称、板块、市值）；
- FR-03：支持财务数据（可选，用于基本面策略）；
- FR-04：数据源可配置（如 akshare/新浪/腾讯等），失败可重试并告警；
- FR-05：数据落库（`daily_quotes` 等表），避免重复拉取。

### 5.2 选股策略（backend/strategy）
- FR-06：策略以插件形式组织，可新增/禁用；
- FR-07：内置至少 1 个示例策略（如均线/量价过滤）；
- FR-08：策略输出候选标的及评分、理由，供 planner 使用。

### 5.3 交易计划生成（backend/planner）
- FR-09：根据候选标的、账户资金、风控规则生成 `trade_plan.json`；
- FR-10：计划包含标的代码、方向（买入/卖出）、数量、价格区间、失效时间、风控条件；
- FR-11：支持「无候选时不生成计划/生成空计划」；
- FR-12：计划写入数据库并保留历史版本，便于追溯。

### 5.4 REST API（backend/api）
- FR-13：健康检查 `GET /api/v1/health`；
- FR-14：获取交易计划 `GET /api/v1/trade-plan?date=YYYY-MM-DD`；
- FR-15：上报成交 `POST /api/v1/trades`；
- FR-16：查询持仓/账户 `GET /api/v1/account`（可选）；
- FR-17：接口鉴权（API Key），日志记录。

### 5.5 数据库（backend/database）
- FR-18：核心表：stocks、daily_quotes、strategies、trade_plans、orders、trades、logs、daily_reports；
- FR-19：提供统一的数据库访问层与迁移脚本；
- FR-20：数据库类型可配置（开发默认 SQLite，生产支持 PostgreSQL/MySQL）。

### 5.6 Windows 执行器（trade-executor）
- FR-21：启动时从后端拉取当日交易计划；
- FR-22：按计划在开盘时间窗口内执行下单；
- FR-23：支持「自动 / 手动确认 / 暂停」三种模式；
- FR-24：下单前校验价格区间与风控条件；
- FR-25：记录本地日志并回传成交结果到后端；
- FR-26：失败自动重试（有限次数），超限后告警并停止。

### 5.7 GUI Agent 集成（trade-executor）
- FR-27：通过屏幕识别（OCR）或控件自动化识别交易软件界面状态；
- FR-28：识别结果用于确认下单结果，避免盲操作；
- FR-29：OCR 失败时进入手动确认模式。

### 5.8 日志与报告
- FR-30：后端与执行器均输出结构化日志（时间、级别、模块、事件）；
- FR-31：每个交易日生成 `daily_report`（计划、成交、盈亏、异常）。

### 5.9 部署与 CI（后续迭代）
- FR-32：GitHub Actions 自动测试（单元测试 + 集成测试）；
- FR-33：Linux 后端提供 Dockerfile 与 docker-compose；
- FR-34：版本化发布（v0.1、v0.2……）。

---

## 6. 非功能需求

- **NFR-01 可靠性**：行情/下单失败可重试；核心流程有日志与告警。
- **NFR-02 安全性**：券商凭据不落明文；API Key 管理；日志脱敏。
- **NFR-03 合规性**：遵守 A 股交易时间与涨跌停规则；不承诺收益；明确风险提示。
- **NFR-04 可测试性**：策略、计划、下单逻辑均可用纯函数/接口测试。
- **NFR-05 可部署性**：后端一键 Docker 部署；执行器提供安装与启动说明。
- **NFR-06 性能**：全市场日线数据获取与选股在 30 分钟内完成。
- **NFR-07 可维护性**：模块独立、接口清晰、文档齐全，支持多 Agent 协作开发。

---

## 7. 数据设计概要（v0.1 先做核心表）

| 表 | 说明 | 关键字段 |
|----|------|---------|
| stocks | 股票基础信息 | code, name, industry, market |
| daily_quotes | 日线行情 | code, date, open, high, low, close, volume, amount |
| strategies | 策略元数据 | name, version, params, enabled |
| trade_plans | 交易计划 | plan_date, code, side, qty, price_min, price_max, expire_at, status |
| orders | 订单记录 | plan_id, code, side, qty, price, status, created_at |
| trades | 成交记录 | order_id, code, qty, price, amount, traded_at |
| logs | 运行日志 | ts, level, module, message |
| daily_reports | 每日报告 | report_date, content(json), created_at |

---

## 8. REST API 概要（v0.1）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/health | 健康检查 |
| GET | /api/v1/trade-plan?date= | 获取某日交易计划 |
| POST | /api/v1/trades | 上报成交 |
| GET | /api/v1/trades?date= | 查询成交记录 |
| GET | /api/v1/account | 账户/持仓（可选） |

统一返回结构：`{ "code": 0, "data": ..., "message": "ok" }`；鉴权：`Authorization: Bearer <api-key>`。

---

## 9. 版本规划

| 版本 | 范围 |
|------|------|
| v0.1 | 项目骨架 + 数据库设计 + 行情获取 + 示例策略 + trade_plan 生成 + REST API + 基础测试 |
| v0.2 | Windows 执行器 + 下单（手动确认模式）+ 日志回传 + 每日报告 |
| v0.3 | GUI Agent 集成（OCR/控件自动化）+ 自动下单模式 |
| v0.4+ | GitHub Actions + Docker 部署 + AI 风控 + 新闻分析 + 参数优化 |
| v1.0 | 全流程闭环：收盘分析 → 次日自动交易 → 全量日志与报告 |

---

## 10. 风险与注意事项

1. **券商接口/自动化风险**：GUI 自动化可能受客户端版本、验证码、风控影响，需预留手动确认兜底。
2. **数据质量**：免费数据源可能缺数/延迟，需校验与补拉。
3. **合规风险**：本系统仅为自动化工具，不构成投资建议；使用者需自行承担交易风险。
4. **AI 生成代码风险**：需人工评审下单、资金相关逻辑，并配套单元测试。
5. **跨平台联调**：Linux↔Windows 通信需统一协议与时间（UTC+8）语义。

---

## 11. v1.0 验收标准

- [ ] 收盘后自动完成数据获取、选股、计划生成并入库；
- [ ] Windows 执行器可按计划完成下单（自动/手动模式均可）并回传成交；
- [ ] 订单、成交、日志、每日报告完整可查；
- [ ] 核心模块均有自动化测试，GitHub Actions 通过；
- [ ] 后端可一键 Docker 部署，README 提供完整上手文档。
