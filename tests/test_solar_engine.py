import pandas as pd

from solpick.solar_engine import (
    SolarCondition,
    azimuth_factor,
    estimate_generation,
    tilt_factor,
)


def sample_profile():
    return pd.DataFrame(
        {
            "region": ["서울"] * 12,
            "month": list(range(1, 13)),
            "daily_ghi_kwh_m2": [3.5] * 12,
            "avg_temp_c": [15.0] * 12,
            "sunshine_hours": [6.0] * 12,
        }
    )


def test_south_is_better_than_north():
    assert azimuth_factor(180) > azimuth_factor(0)


def test_optimal_tilt_is_better_than_flat_extreme():
    assert tilt_factor(30) >= tilt_factor(80)


def test_generation_increases_with_area():
    profile = sample_profile()

    small = SolarCondition("서울", 20, 0.75, 30, 180, "none", 0.2, 0.82)
    large = SolarCondition("서울", 40, 0.75, 30, 180, "none", 0.2, 0.82)

    small_result = estimate_generation(profile, small)
    large_result = estimate_generation(profile, large)

    assert large_result["annual_generation_kwh"] > small_result["annual_generation_kwh"]


def test_generation_is_non_negative():
    profile = sample_profile()
    condition = SolarCondition("서울", 30, 0.75, 30, 180, "none", 0.2, 0.82)
    result = estimate_generation(profile, condition)
    assert result["annual_generation_kwh"] >= 0
    assert result["capacity_kwp"] > 0
