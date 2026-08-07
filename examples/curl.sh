#!/usr/bin/env bash
# 后端 API 调用示例
set -euo pipefail

API=http://localhost:8000/api/v1
KEY=dev-key

echo "== 健康检查 =="
curl -s "$API/health"
echo

echo "== 查询 2026-08-07 交易计划 =="
curl -s "$API/trade-plans?date=2026-08-07" -H "Authorization: Bearer $KEY"
echo

echo "== 上报成交 =="
curl -s -X POST "$API/trades" \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" \
  -d '{"client_request_id":"demo-0001","item_id":10,"order_no":"BK001","code":"600000","side":"buy","quantity":100,"price":10.62,"traded_at":"2026-08-08T09:31:05+08:00","commission":5.0}'
echo
