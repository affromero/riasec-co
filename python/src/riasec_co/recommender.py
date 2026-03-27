"""Program recommendation engine."""

from __future__ import annotations

import math

import polars as pl

from riasec_co.data import Programs, load_mapping
from riasec_co.scoring import RIASEC_TYPES, cosine_similarity

VIRTUAL_MODALITIES = {"Virtual", "A distancia", "Virtual-A distancia"}


def _field_to_profile(
    cine_amplio: str,
    mapping: dict[str, dict],
) -> dict[str, float]:
    """Build a RIASEC profile vector for a CINE broad field."""
    profile = {t: 0.0 for t in RIASEC_TYPES}
    for riasec_type in RIASEC_TYPES:
        entry = mapping.get(riasec_type, {})
        for field_entry in entry.get("fields", []):
            if field_entry["cine_amplio"] == cine_amplio:
                profile[riasec_type] = field_entry["weight"]
    return profile


def recommend(
    profile: dict[str, float],
    programs: pl.DataFrame | None = None,
    mapping: dict[str, dict] | None = None,
    *,
    departments: list[str] | None = None,
    active_only: bool = True,
    nivel_formacion: list[str] | None = None,
    modalidad: list[str] | None = None,
    enrollment_weight: float = -0.3,
    regional_boost: float = 1.0,
    virtual_boost: float = 1.0,
    limit: int = 20,
) -> pl.DataFrame:
    """Recommend programs based on a RIASEC profile.

    Returns a Polars DataFrame with columns from the program data plus
    'score', 'similarity', and 'matching_types'.
    """
    if programs is None:
        programs = Programs.load()
    if mapping is None:
        mapping = load_mapping()

    df = programs

    # Apply filters
    if active_only:
        df = df.filter(pl.col("estado") == "Activo")
    if departments:
        df = df.filter(pl.col("departamento").is_in(departments))
    if nivel_formacion:
        df = df.filter(pl.col("nivel_formacion").is_in(nivel_formacion))
    if modalidad:
        df = df.filter(pl.col("modalidad").is_in(modalidad))

    # Pre-compute field profiles
    field_profiles: dict[str, dict[str, float]] = {}
    for field_name in df.get_column("cine_amplio").drop_nulls().unique().to_list():
        field_profiles[field_name] = _field_to_profile(field_name, mapping)

    # Compute field counts for enrollment-based priors
    all_active = programs.filter(pl.col("estado") == "Activo")
    total_programs = len(all_active)
    field_counts: dict[str, int] = {}
    for row in all_active.group_by("cine_amplio").len().iter_rows():
        field_counts[row[0]] = row[1]

    regional_set = set(departments) if departments else set()

    # Score each row
    scores = []
    similarities = []
    matching_types_list = []

    for row in df.iter_rows(named=True):
        cine = row.get("cine_amplio", "")
        field_profile = field_profiles.get(cine)

        if not field_profile or all(v == 0 for v in field_profile.values()):
            scores.append(0.0)
            similarities.append(0.0)
            matching_types_list.append("")
            continue

        sim = cosine_similarity(profile, field_profile)
        if sim == 0:
            scores.append(0.0)
            similarities.append(0.0)
            matching_types_list.append("")
            continue

        # Enrollment-based prior
        fc = field_counts.get(cine, 1)
        enrollment_factor = 1 + enrollment_weight * math.log(total_programs / fc)

        # Regional boost
        is_regional = 1 if row.get("departamento", "") in regional_set else 0
        regional_factor = 1 + regional_boost * is_regional

        # Virtual boost
        is_virtual = 1 if row.get("modalidad", "") in VIRTUAL_MODALITIES else 0
        virtual_factor = 1 + virtual_boost * is_virtual

        score = sim * enrollment_factor * regional_factor * virtual_factor
        matching = [t for t in RIASEC_TYPES if field_profile[t] > 0]

        scores.append(score)
        similarities.append(sim)
        matching_types_list.append(",".join(matching))

    result = df.with_columns(
        pl.Series("score", scores),
        pl.Series("similarity", similarities),
        pl.Series("matching_types", matching_types_list),
    )

    # Sort, deduplicate, re-sort, limit
    result = (
        result
        .sort("score", descending=True)
        .unique(subset=["codigo_snies"], keep="first")
        .sort("score", descending=True)
        .head(limit)
    )

    return result
