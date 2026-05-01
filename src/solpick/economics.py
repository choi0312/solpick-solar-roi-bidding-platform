from __future__ import annotations

from typing import Optional


def calculate_economics(
    capacity_kwp: float,
    annual_generation_kwh: float,
    monthly_bill_krw: float,
    electricity_price_krw_per_kwh: float,
    export_price_krw_per_kwh: float,
    install_cost_per_kw: float,
    subsidy_krw: float,
    maintenance_ratio: float = 0.01,
    analysis_years: int = 25,
) -> dict:
    gross_capex = max(0.0, capacity_kwp * install_cost_per_kw)
    subsidy = min(max(0.0, subsidy_krw), gross_capex)
    net_capex = max(gross_capex - subsidy, 0.0)

    annual_consumption_kwh = (monthly_bill_krw * 12.0) / electricity_price_krw_per_kwh

    self_consumed_kwh = min(annual_generation_kwh, annual_consumption_kwh)
    surplus_kwh = max(annual_generation_kwh - annual_consumption_kwh, 0.0)

    annual_savings = self_consumed_kwh * electricity_price_krw_per_kwh
    annual_export_revenue = surplus_kwh * export_price_krw_per_kwh
    annual_maintenance = gross_capex * maintenance_ratio

    annual_benefit = max(0.0, annual_savings + annual_export_revenue - annual_maintenance)

    payback_years: Optional[float]
    if annual_benefit > 0:
        payback_years = net_capex / annual_benefit
    else:
        payback_years = None

    if net_capex > 0:
        roi_25yr = ((annual_benefit * analysis_years - net_capex) / net_capex) * 100.0
    else:
        roi_25yr = None

    return {
        "gross_capex_krw": round(gross_capex),
        "subsidy_krw": round(subsidy),
        "net_capex_krw": round(net_capex),
        "annual_consumption_kwh": round(annual_consumption_kwh, 2),
        "self_consumed_kwh": round(self_consumed_kwh, 2),
        "surplus_kwh": round(surplus_kwh, 2),
        "annual_savings_krw": round(annual_savings),
        "annual_export_revenue_krw": round(annual_export_revenue),
        "annual_maintenance_krw": round(annual_maintenance),
        "annual_benefit_krw": round(annual_benefit),
        "payback_years": round(payback_years, 2) if payback_years is not None else None,
        "roi_25yr_percent": round(roi_25yr, 2) if roi_25yr is not None else None,
    }
