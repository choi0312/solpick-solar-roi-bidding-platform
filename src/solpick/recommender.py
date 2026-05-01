from __future__ import annotations

from typing import List

import numpy as np
import pandas as pd

from solpick.economics import calculate_economics
from solpick.solar_engine import SolarCondition, estimate_generation
from solpick.subsidies import match_best_subsidy


def _minmax(values: pd.Series, inverse: bool = False) -> pd.Series:
    values = values.astype(float)
    vmin = values.min()
    vmax = values.max()

    if np.isclose(vmax, vmin):
        scores = pd.Series(np.ones(len(values)), index=values.index)
    else:
        scores = (values - vmin) / (vmax - vmin)

    if inverse:
        scores = 1.0 - scores

    return scores.clip(0.0, 1.0)


def _region_score(service_regions: str, user_region: str) -> float:
    regions = [r.strip() for r in str(service_regions).split("|")]
    if user_region in regions:
        return 1.0
    if "전국" in regions:
        return 0.8
    return 0.35


def recommend_installers(
    installers: pd.DataFrame,
    regional_profile: pd.DataFrame,
    subsidy_rules: pd.DataFrame,
    request,
) -> List[dict]:
    df = installers.copy()

    df["cost_score"] = _minmax(df["cost_per_kw"], inverse=True)
    df["efficiency_score"] = _minmax(df["module_efficiency"])
    df["pr_score"] = _minmax(df["performance_ratio"])
    df["performance_score"] = 0.55 * df["efficiency_score"] + 0.45 * df["pr_score"]

    df["rating_score"] = df["rating"].astype(float) / 5.0
    df["as_score_norm"] = df["as_score"].astype(float) / 100.0
    df["sentiment_score"] = df["review_sentiment"].astype(float) / 100.0
    df["reliability_score"] = (
        0.40 * df["rating_score"]
        + 0.35 * df["as_score_norm"]
        + 0.25 * df["sentiment_score"]
    )

    df["warranty_score"] = (df["warranty_years"].astype(float) / 15.0).clip(0.0, 1.0)
    df["region_score"] = df["service_regions"].apply(
        lambda value: _region_score(value, request.region)
    )

    df["score"] = (
        0.35 * df["cost_score"]
        + 0.25 * df["performance_score"]
        + 0.20 * df["reliability_score"]
        + 0.10 * df["warranty_score"]
        + 0.10 * df["region_score"]
    )

    results: List[dict] = []

    for _, row in df.sort_values("score", ascending=False).iterrows():
        condition = SolarCondition(
            region=request.region,
            roof_area_m2=request.roof_area_m2,
            roof_usage_ratio=request.roof_usage_ratio,
            tilt_deg=request.tilt_deg,
            azimuth_deg=request.azimuth_deg,
            shading_level=request.shading_level,
            module_efficiency=float(row["module_efficiency"]),
            performance_ratio=float(row["performance_ratio"]),
        )

        generation = estimate_generation(regional_profile, condition)
        subsidy = match_best_subsidy(
            subsidy_rules=subsidy_rules,
            region=request.region,
            user_type=request.user_type,
            capacity_kwp=float(generation["capacity_kwp"]),
        )
        economics = calculate_economics(
            capacity_kwp=float(generation["capacity_kwp"]),
            annual_generation_kwh=float(generation["annual_generation_kwh"]),
            monthly_bill_krw=request.monthly_bill_krw,
            electricity_price_krw_per_kwh=request.electricity_price_krw_per_kwh,
            export_price_krw_per_kwh=request.export_price_krw_per_kwh,
            install_cost_per_kw=float(row["cost_per_kw"]),
            subsidy_krw=float(subsidy["amount_krw"]),
        )

        budget_match = True
        if request.budget_krw is not None:
            budget_match = economics["net_capex_krw"] <= request.budget_krw

        results.append(
            {
                "installer_id": str(row["installer_id"]),
                "name": str(row["name"]),
                "score": round(float(row["score"]) * 100.0, 2),
                "region_match": round(float(row["region_score"]), 2),
                "cost_per_kw": round(float(row["cost_per_kw"])),
                "module_efficiency": round(float(row["module_efficiency"]), 3),
                "performance_ratio": round(float(row["performance_ratio"]), 3),
                "warranty_years": int(row["warranty_years"]),
                "rating": float(row["rating"]),
                "as_score": int(row["as_score"]),
                "budget_match": budget_match,
                "estimated_capacity_kwp": generation["capacity_kwp"],
                "annual_generation_kwh": generation["annual_generation_kwh"],
                "monthly_generation": generation["monthly_generation"],
                "subsidy": subsidy,
                **economics,
            }
        )

    return results[: request.top_n]
