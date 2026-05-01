from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def data_path(filename: str) -> Path:
    return PROJECT_ROOT / "data" / filename


@lru_cache(maxsize=1)
def load_regional_profile() -> pd.DataFrame:
    path = data_path("regional_solar_profile.csv")
    if not path.exists():
        raise FileNotFoundError(f"Missing data file: {path}")
    return pd.read_csv(path)


@lru_cache(maxsize=1)
def load_installers() -> pd.DataFrame:
    path = data_path("installers.csv")
    if not path.exists():
        raise FileNotFoundError(f"Missing data file: {path}")
    return pd.read_csv(path)


@lru_cache(maxsize=1)
def load_subsidy_rules() -> pd.DataFrame:
    path = data_path("subsidy_rules.csv")
    if not path.exists():
        raise FileNotFoundError(f"Missing data file: {path}")
    return pd.read_csv(path)
