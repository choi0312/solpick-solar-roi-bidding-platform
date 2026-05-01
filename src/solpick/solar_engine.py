from __future__ import annotations

import calendar
from dataclasses import dataclass
from typing import Any, Dict

import pandas as pd


SHADING_FACTORS = {
    "none": 1.00,
    "low": 0.93,
    "medium": 0.84,
    "high": 0.70,
}


@dataclass(frozen=True)
class SolarCondition:
    region: str
    roof_area_m2: float
    roof_usage_ratio: float
    tilt_deg: float
    azimuth_deg: float
    shading_level: str
    module_efficiency: float
    performance_ratio: float


def azimuth_factor(azimuth_deg: float) -> float:
    """Return south-facing correction factor.

    180 degrees is assumed to be south-facing. The factor is smoothly penalized
    as the panel orientation moves away from south.
    """
    diff = abs(((azimuth_deg - 180.0 + 180.0) % 360.0) - 180.0)
    return max(0.55, 1.0 - 0.35 * (diff / 180.0) ** 1.3)


def tilt_factor(tilt_deg: float, optimal_tilt: float = 30.0) -> float:
    """Return tilt correction factor around a 30-degree reference."""
    diff = abs(tilt_deg - optimal_tilt)
    return max(0.75, 1.0 - 0.00025 * diff * diff)


def temperature_factor(avg_temp_c: float) -> float:
    """Simple PV temperature derating proxy.

    The coefficient is intentionally conservative. It does not replace a full
    cell-temperature model but prevents unrealistically identical output across
    very different seasonal temperatures.
    """
    if avg_temp_c <= 25:
        return min(1.03, 1.0 + 0.001 * (25 - avg_temp_c))
    return max(0.92, 1.0 - 0.004 * (avg_temp_c - 25))


def estimate_capacity_kwp(
    roof_area_m2: float,
    roof_usage_ratio: float,
    module_efficiency: float,
) -> float:
    """Estimate installable PV capacity.

    Under STC, 1m² receives 1kW of irradiance. Therefore,
    area × module efficiency approximates kWp capacity.
    """
    usable_area = roof_area_m2 * roof_usage_ratio
    return max(0.0, usable_area * module_efficiency)


def estimate_generation(
    regional_profile: pd.DataFrame,
    condition: SolarCondition,
) -> Dict[str, Any]:
    region_df = regional_profile[regional_profile["region"] == condition.region].copy()

    if region_df.empty:
        region_df = regional_profile[regional_profile["region"] == "서울"].copy()

    region_df = region_df.sort_values("month")

    capacity_kwp = estimate_capacity_kwp(
        roof_area_m2=condition.roof_area_m2,
        roof_usage_ratio=condition.roof_usage_ratio,
        module_efficiency=condition.module_efficiency,
    )

    orientation_factor = (
        azimuth_factor(condition.azimuth_deg)
        * tilt_factor(condition.tilt_deg)
        * SHADING_FACTORS.get(condition.shading_level, SHADING_FACTORS["low"])
    )

    monthly = []
    annual_generation = 0.0

    for _, row in region_df.iterrows():
        month = int(row["month"])
        days = calendar.monthrange(2025, month)[1]
        monthly_ghi = float(row["daily_ghi_kwh_m2"]) * days

        temp_adj = temperature_factor(float(row["avg_temp_c"]))

        generation = (
            monthly_ghi
            * capacity_kwp
            * condition.performance_ratio
            * orientation_factor
            * temp_adj
        )

        generation = max(0.0, generation)
        annual_generation += generation

        monthly.append(
            {
                "month": month,
                "monthly_ghi_kwh_m2": round(monthly_ghi, 2),
                "generation_kwh": round(generation, 2),
            }
        )

    specific_yield = annual_generation / capacity_kwp if capacity_kwp > 0 else 0.0

    return {
        "capacity_kwp": round(capacity_kwp, 3),
        "annual_generation_kwh": round(annual_generation, 2),
        "specific_yield_kwh_per_kwp": round(specific_yield, 2),
        "orientation_factor": round(orientation_factor, 3),
        "monthly_generation": monthly,
    }
