# REST API 设计文档（OpenAPI）

> 版本：v0.1（草稿）　|　日期：2026-08-07　|　状态：待评审
> 关联文档：[系统架构设计文档.md](系统架构设计文档.md)、[数据库设计文档.md](数据库设计文档.md)
> 机器可读规范：[openapi.yaml](openapi.yaml)（OpenAPI 3.0.3）

---

## 1. 通用约定

- Base URL：`/api/v1`（开发 `http://localhost:8000`，生产 HTTPS）；
- 数据格式：JSON（UTF-8）；
- 时区：Asia/Shanghai；日期 `YYYY-MM-DD`；时间 ISO8601（带时区偏移，如 `2026-08-08T09:31:05+08:00`）；
- 鉴权：`Authorization: Bearer <api-key>`（`/health` 除外）；
- 分页：统一使用 `limit`（默认 50，最大 200）与 `offset`；
- 幂等：`POST /trades` 使用 `client_request_id` 防重复上报。

---

## 2. 统一响应结构

```json
{
  "code": 0,
  "message": "ok",
  "data": { }
}
```

业务错误码（与架构文档一致）：

| code | HTTP | 含义 |
|------|------|------|
| 0 | 200/201 | 成功 |
| 1001 | 401 | 鉴权失败 |
| 1002 | 422 | 参数错误 |
| 2001 | 404 | 计划不存在 |
| 2002 | 409 | 计划已过期或不可执行 |
| 3001 | 404 | 行情数据缺失 |
| 4001 | 409 | 重复上报 |
| 5000 | 500 | 服务器内部错误 |

---

## 3. 端点总览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /health | 健康检查 |
| GET | /trade-plans?date=&status= | 查询交易计划（按日） |
| GET | /trade-plans/{plan_id} | 计划详情（含明细） |
| POST | /trades | 上报成交（执行器） |
| GET | /trades?date=&code= | 查询成交记录 |
| GET | /trades/{trade_id} | 成交详情 |
| GET | /account?date= | 账户与持仓快照 |
| GET | /daily-reports/{report_date} | 每日报告 |
| GET | /strategies | 策略列表 |
| POST | /executor/heartbeat | 执行器心跳（监控） |

---

## 4. 详细接口说明

### 4.1 GET /health
健康检查（无需鉴权）。

响应 200：
```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "status": "ok",
    "version": "0.1.0",
    "time": "2026-08-07T09:00:00+08:00"
  }
}
```

### 4.2 GET /trade-plans
查询某日交易计划（含全部明细，供执行器使用）。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| date | string(YYYY-MM-DD) | 是 | 计划日期 |
| status | string | 否 | draft / published / executing / done / cancelled |
| limit | integer | 否 | 默认 50 |
| offset | integer | 否 | 默认 0 |

响应 200：
```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "plans": [
      {
        "plan_id": 1,
        "plan_date": "2026-08-07",
        "status": "published",
        "items": [
          {
            "item_id": 10,
            "code": "600000",
            "name": "浦发银行",
            "side": "buy",
            "quantity": 100,
            "price_min": 10.5,
            "price_max": 11.0,
            "expire_at": "2026-08-08T09:35:00+08:00",
            "status": "pending",
            "reason": "均线多头排列"
          }
        ]
      }
    ],
    "total": 1
  }
}
```

### 4.3 GET /trade-plans/{plan_id}
计划详情，返回结构同上（单条）。

### 4.4 POST /trades
执行器上报成交，`client_request_id` 保证幂等。

请求体：
```json
{
  "client_request_id": "exec-01-20260807-0001",
  "item_id": 10,
  "order_no": "BK20260807123456",
  "code": "600000",
  "side": "buy",
  "quantity": 100,
  "price": 10.62,
  "traded_at": "2026-08-08T09:31:05+08:00",
  "commission": 5.0
}
```

响应 201：
```json
{
  "code": 0,
  "message": "ok",
  "data": { "trade_id": 88 }
}
```

### 4.5 GET /trades
查询成交记录。参数：`date`、`code`、`limit`、`offset`。

响应 data：
```json
{
  "trades": [
    {
      "trade_id": 88,
      "order_id": 12,
      "client_request_id": "exec-01-20260807-0001",
      "code": "600000",
      "side": "buy",
      "quantity": 100,
      "price": 10.62,
      "amount": 1062.0,
      "commission": 5.0,
      "traded_at": "2026-08-08T09:31:05+08:00"
    }
  ],
  "total": 1
}
```

### 4.6 GET /trades/{trade_id}
单条成交详情，结构同上。

### 4.7 GET /account?date=
账户快照：总资产、可用资金、持仓市值、持仓明细。

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "snapshot_date": "2026-08-07",
    "total_asset": 100000.0,
    "available_cash": 50000.0,
    "market_value": 50000.0,
    "positions": [
      { "code": "600000", "quantity": 800, "cost_price": 10.0, "market_price": 10.62 }
    ]
  }
}
```

### 4.8 GET /daily-reports/{report_date}
每日报告（计划数、成交数、盈亏、异常等摘要）。

### 4.9 GET /strategies
策略列表：
```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "strategies": [
      { "strategy_id": 1, "name": "ma_cross", "version": "0.1.0", "enabled": true }
    ],
    "total": 1
  }
}
```

### 4.10 POST /executor/heartbeat
执行器心跳（监控用）：
```json
{
  "executor_id": "win-01",
  "status": "running",
  "message": ""
}
```

---

## 5. 安全

- 所有端点（除 `/health` 外）需要 `Authorization: Bearer <api-key>`；
- 生产环境强制 HTTPS；
- 也支持 `X-API-Key` 请求头（二选一），由后端统一校验。

---

## 6. 客户端示例

curl：
```bash
curl -s http://localhost:8000/api/v1/trade-plans?date=2026-08-07 \
  -H "Authorization: Bearer <api-key>"
```

Python：
```python
import requests

resp = requests.get(
    "http://localhost:8000/api/v1/trade-plans",
    params={"date": "2026-08-07"},
    headers={"Authorization": "Bearer <api-key>"},
)
print(resp.json())
```

---

## 7. OpenAPI 规范

完整的机器可读规范见 [openapi.yaml](openapi.yaml)，可直接在 https://editor.swagger.io 打开预览，或由 FastAPI 在 `/docs` 中渲染。
