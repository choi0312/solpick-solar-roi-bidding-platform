from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    region: str = Field(default="서울")
    user_type: Literal["residential", "small_business", "commercial"] = "residential"

    roof_area_m2: float = Field(default=30.0, gt=0, le=10000)
    roof_usage_ratio: float = Field(default=0.75, gt=0, le=1.0)

    tilt_deg: float = Field(default=30.0, ge=0, le=90)
    azimuth_deg: float = Field(default=180.0, ge=0, le=360)
    shading_level: Literal["none", "low", "medium", "high"] = "low"

    monthly_bill_krw: float = Field(default=120000, gt=0)
    electricity_price_krw_per_kwh: float = Field(default=180, gt=0)
    export_price_krw_per_kwh: float = Field(default=80, ge=0)

    budget_krw: Optional[float] = Field(default=None, ge=0)
    top_n: int = Field(default=3, ge=1, le=10)


class InstallerRecommendation(BaseModel):
    installer_id: str
    name: str
    score: float
    estimated_capacity_kwp: float
    annual_generation_kwh: float
    gross_capex_krw: float
    subsidy_krw: float
    net_capex_krw: float
    annual_benefit_krw: float
    payback_years: Optional[float]
    roi_25yr_percent: Optional[float]


class AnalysisResponse(BaseModel):
    region: str
    capacity_kwp: float
    annual_generation_kwh: float
    monthly_generation: list[dict]
    best_subsidy: dict
    top_installers: list[InstallerRecommendation]
