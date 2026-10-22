import pandas as pd
import pytest


@pytest.fixture
def sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "name": ["a", "b", None, "d", "a"],
            "value": [10.0, 12.0, 11.0, 1000.0, 9.0],
            "category": ["x", "y", "x", "y", "x"],
        }
    )