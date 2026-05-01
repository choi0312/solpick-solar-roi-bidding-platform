from __future__ import annotations

import pandas as pd


def match_best_subsidy(
    subsidy_rules: pd.DataFrame,
    region: str,
    user_type: str,
    capacity_kwp: float,
) -> dict:
    candidates = subsidy_rules[
        ((subsidy_rules["region"] == region) | (subsidy_rules["region"] == "전국"))
        & (
            (subsidy_rules["user_type"] == user_type)
            | (subsidy_rules["user_type"] == "all")
        )
    ].copy()

    if candidates.empty:
        return {
            "region": "해당 없음",
            "user_type": user_type,
            "subsidy_per_kw": 0,
            "subsidy_cap": 0,
            "amount_krw": 0,
            "description": "적용 가능한 지원금 규칙이 없습니다.",
        }

    candidates["amount_krw"] = candidates.apply(
        lambda row: min(
            float(row["subsidy_per_kw"]) * capacity_kwp,
            float(row["subsidy_cap"]),
        ),
        axis=1,
    )

    best = candidates.sort_values("amount_krw", ascending=False).iloc[0]

    return {
        "region": str(best["region"]),
        "user_type": str(best["user_type"]),
        "subsidy_per_kw": round(float(best["subsidy_per_kw"])),
        "subsidy_cap": round(float(best["subsidy_cap"])),
        "amount_krw": round(float(best["amount_krw"])),
        "description": str(best["description"]),
    }
