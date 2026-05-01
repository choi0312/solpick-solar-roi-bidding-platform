from solpick.data_loader import load_installers, load_regional_profile, load_subsidy_rules
from solpick.recommender import recommend_installers
from solpick.schemas import AnalysisRequest


def test_recommender_returns_top_n():
    request = AnalysisRequest(region="서울", roof_area_m2=30, top_n=3)

    results = recommend_installers(
        installers=load_installers(),
        regional_profile=load_regional_profile(),
        subsidy_rules=load_subsidy_rules(),
        request=request,
    )

    assert len(results) == 3
    assert results[0]["score"] >= results[-1]["score"]
