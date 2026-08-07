"""控制台界面：展示计划、手动确认。"""

from __future__ import annotations

from shared.models import TradePlan


def print_plan(plan: TradePlan) -> None:
    print(f"交易计划 {plan.plan_date} [{plan.status.value}]")
    for item in plan.items:
        price_range = (
            f"{item.price_min}~{item.price_max}"
            if item.price_min or item.price_max
            else "-"
        )
        line = (
            f"  - {item.code} {item.side.value} {item.quantity}股  区间: {price_range}  "
            f"理由: {item.reason or '-'}"
        )
        print(line)


def confirm_plan() -> bool:
    while True:
        answer = input("是否执行以上计划？(y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
