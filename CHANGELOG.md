# Changelog

## [1.0.0] - 2026-08-07

### 里程碑：v1.0（收盘分析 → 次日自动交易 → 全量日志报告）

#### 新增
- v0.4 订单/成交状态同步：`/orders` 接口（幂等上报）、`trades.order_id` 关联、Alembic 迁移 `bf9e8f205499`
- v0.3 OCR 成交确认：Tesseract / PaddleOCR / Fake 引擎 + 成交文本解析（全部成交/部分成交/废单/未成交）+ `--ocr-check` CLI
- v0.2 券商适配层：Paper 模拟撮合（价格区间校验/风控拒单/部分成交）、Client(pywinauto) 脚手架、PySide6 桌面界面
- v0.1 项目骨架：FastAPI 后端 + 数据/策略/计划流水线 + REST API + CI

#### 修复
- `save_trade` 未持久化 `order_id`（v0.4 关联遗漏）
- OCR 解析把「全部成交」误判为「部分成交」（`部成` 子串）
- `.gitignore` 的 `data/` 规则误伤 `app/data` 模块
- SQLite 迁移：唯一约束需 batch 模式；`DROP NOT NULL` 不支持

#### 测试
- 后端 21 个、执行器 32 个、ruff 全绿、CI（Python 3.11/3.12）通过