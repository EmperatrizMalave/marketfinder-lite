"""Exportación básica CSV / Excel del ranking (Etapa 1)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from marketfinder.utils.paths import exports_dir


def ranking_to_dataframe(rows: Iterable[dict[str, Any]]) -> pd.DataFrame:
    df = pd.DataFrame(list(rows))
    if df.empty:
        df = pd.DataFrame(
            columns=[
                "rank",
                "product",
                "score",
                "confidence",
                "band",
                "qty",
                "capital",
                "notes",
            ]
        )
    return df


def export_ranking_csv(
    rows: Iterable[dict[str, Any]],
    path: Path | str | None = None,
    *,
    data_dir: Path | str | None = None,
) -> Path:
    dest = Path(path) if path else exports_dir(data_dir) / "ranking.csv"
    dest.parent.mkdir(parents=True, exist_ok=True)
    df = ranking_to_dataframe(rows)
    df.to_csv(dest, index=False, encoding="utf-8-sig")
    return dest


def export_ranking_xlsx(
    rows: Iterable[dict[str, Any]],
    path: Path | str | None = None,
    *,
    data_dir: Path | str | None = None,
) -> Path:
    dest = Path(path) if path else exports_dir(data_dir) / "ranking.xlsx"
    dest.parent.mkdir(parents=True, exist_ok=True)
    df = ranking_to_dataframe(rows)
    df.to_excel(dest, index=False, engine="openpyxl")
    return dest
