from solpick.economics import calculate_economics


def test_economics_non_negative():
    result = calculate_economics(
        capacity_kwp=5,
        annual_generation_kwh=6000,
        monthly_bill_krw=120000,
        electricity_price_krw_per_kwh=180,
        export_price_krw_per_kwh=80,
        install_cost_per_kw=1500000,
        subsidy_krw=2000000,
    )

    assert result["gross_capex_krw"] >= 0
    assert result["net_capex_krw"] >= 0
    assert result["annual_benefit_krw"] >= 0


def test_subsidy_cannot_exceed_gross_capex():
    result = calculate_economics(
        capacity_kwp=2,
        annual_generation_kwh=2500,
        monthly_bill_krw=80000,
        electricity_price_krw_per_kwh=180,
        export_price_krw_per_kwh=80,
        install_cost_per_kw=1000000,
        subsidy_krw=999999999,
    )

    assert result["net_capex_krw"] == 0
