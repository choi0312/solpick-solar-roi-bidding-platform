from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from solpick.data_loader import load_installers, load_regional_profile, load_subsidy_rules
from solpick.recommender import recommend_installers
from solpick.schemas import AnalysisRequest
from solpick.solar_engine import SolarCondition, estimate_generation
from solpick.subsidies import match_best_subsidy

app = FastAPI(
    title="SOLPICK Solar ROI Platform",
    description="Solar generation, ROI analysis, subsidy matching, and installer recommendation prototype.",
    version="0.1.0",
)

app.mount("/static", StaticFiles(directory=PROJECT_ROOT / "app" / "static"), name="static")


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return (PROJECT_ROOT / "app" / "static" / "index.html").read_text(encoding="utf-8")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/defaults")
def defaults() -> dict:
    profile = load_regional_profile()
    return {
        "regions": sorted(profile["region"].unique().tolist()),
        "user_types": [
            {"value": "residential", "label": "주거용"},
            {"value": "small_business", "label": "소규모 사업자"},
            {"value": "commercial", "label": "상업·산업용"},
        ],
        "shading_levels": [
            {"value": "none", "label": "거의 없음"},
            {"value": "low", "label": "약간 있음"},
            {"value": "medium", "label": "보통"},
            {"value": "high", "label": "많음"},
        ],
    }


@app.post("/api/analyze")
def analyze(request: AnalysisRequest) -> dict:
    profile = load_regional_profile()
    installers = load_installers()
    subsidy_rules = load_subsidy_rules()

    baseline_condition = SolarCondition(
        region=request.region,
        roof_area_m2=request.roof_area_m2,
        roof_usage_ratio=request.roof_usage_ratio,
        tilt_deg=request.tilt_deg,
        azimuth_deg=request.azimuth_deg,
        shading_level=request.shading_level,
        module_efficiency=0.20,
        performance_ratio=0.82,
    )
    baseline_generation = estimate_generation(profile, baseline_condition)
    best_subsidy = match_best_subsidy(
        subsidy_rules=subsidy_rules,
        region=request.region,
        user_type=request.user_type,
        capacity_kwp=float(baseline_generation["capacity_kwp"]),
    )

    top_installers = recommend_installers(
        installers=installers,
        regional_profile=profile,
        subsidy_rules=subsidy_rules,
        request=request,
    )

    return {
        "input": request.model_dump(),
        "baseline": baseline_generation,
        "best_subsidy": best_subsidy,
        "top_installers": top_installers,
    }
