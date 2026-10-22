"""Load CSV/Excel files into pandas DataFrames with validation."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Union

import pandas as pd

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


class DataLoadError(Exception):
    """Raised when a file cannot be loaded."""


def load_dataframe(
    path: Union[str, Path],
    sheet_name: Union[str, int, None] = None,
    **read_kwargs,
) -> pd.DataFrame:
    """Load a CSV or Excel file into a DataFrame.

    Parameters
    ----------
    path:
        Path to the file.
    sheet_name:
        For Excel only: sheet name or index. Ignored for CSV.
    **read_kwargs:
        Extra keyword args forwarded to pandas readers.
    """
    path = Path(path)
    if not path.exists():
        raise DataLoadError(f"File not found: {path}")
    if not path.is_file():
        raise DataLoadError(f"Not a file: {path}")

    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise DataLoadError(
            f"Unsupported extension '{ext}'. Allowed: {sorted(SUPPORTED_EXTENSIONS)}"
        )

    logger.info("Loading %s", path)
    try:
        if ext == ".csv":
            df = pd.read_csv(path, **read_kwargs)
        else:
            df = pd.read_excel(path, sheet_name=sheet_name or 0, **read_kwargs)
    except Exception as exc:  # pragma: no cover - passthrough of pandas errors
        raise DataLoadError(f"Failed to parse {path}: {exc}") from exc

    if df.empty:
        raise DataLoadError(f"File {path} produced an empty DataFrame")

    logger.info("Loaded %d rows x %d columns", *df.shape)
    return df