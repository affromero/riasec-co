"""Data loaders for SNIES programs and IPIP items."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import polars as pl

# Canonical data directory: relative to this file → ../../data/canonical
_DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "canonical"


@dataclass(frozen=True)
class Item:
    """A single IPIP RIASEC item."""

    id: str
    type: str
    text: str
    keyed: str


def _find_data_dir() -> Path:
    """Find the canonical data directory."""
    if _DATA_DIR.exists():
        return _DATA_DIR
    # Fallback: check relative to cwd
    alt = Path.cwd() / "data" / "canonical"
    if alt.exists():
        return alt
    raise FileNotFoundError(
        f"Cannot find canonical data directory. Tried: {_DATA_DIR}, {alt}"
    )


def load_items(language: str = "es") -> list[Item]:
    """Load IPIP RIASEC items for the given language."""
    data_dir = _find_data_dir()
    path = data_dir / f"items_{language}.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [Item(**item) for item in raw["items"]]


def load_mapping() -> dict[str, dict]:
    """Load the RIASEC → CINE field mapping."""
    data_dir = _find_data_dir()
    path = data_dir / "mapping.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    return raw["mapping"]


class Programs:
    """Loader for SNIES program data as Polars DataFrames."""

    _cache: pl.DataFrame | None = None

    @classmethod
    def load(cls) -> pl.DataFrame:
        """Load all programs from canonical CSV into a Polars DataFrame."""
        if cls._cache is not None:
            return cls._cache

        data_dir = _find_data_dir()
        path = data_dir / "programs.csv"

        df = pl.read_csv(
            path,
            infer_schema_length=5000,
            null_values=[""],
            schema_overrides={
                "codigo_snies": pl.Int64,
                "creditos": pl.Int64,
                "periodos_duracion": pl.Int64,
                "costo_matricula": pl.Float64,
            },
        )
        cls._cache = df
        return df

    @classmethod
    def active(cls) -> pl.DataFrame:
        """Load only active programs."""
        return cls.load().filter(pl.col("estado") == "Activo")

    @classmethod
    def departments(cls) -> list[str]:
        """Get unique departments."""
        return sorted(
            cls.load()
            .get_column("departamento")
            .drop_nulls()
            .unique()
            .to_list()
        )

    @classmethod
    def cine_fields(cls) -> list[str]:
        """Get unique CINE broad fields."""
        return sorted(
            cls.load()
            .get_column("cine_amplio")
            .drop_nulls()
            .unique()
            .to_list()
        )
