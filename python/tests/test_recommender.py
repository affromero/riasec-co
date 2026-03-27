"""Tests for the recommendation engine."""

import pytest
import polars as pl

from riasec_co.recommender import recommend
from riasec_co.data import Programs

INVESTIGATIVE_PROFILE = {
    "R": 0.05, "I": 0.55, "A": 0.05,
    "S": 0.10, "E": 0.10, "C": 0.15,
}

ARTISTIC_PROFILE = {
    "R": 0.05, "I": 0.05, "A": 0.55,
    "S": 0.15, "E": 0.10, "C": 0.10,
}


def test_recommend_returns_sorted_dataframe():
    results = recommend(INVESTIGATIVE_PROFILE, limit=10)
    assert isinstance(results, pl.DataFrame)
    assert len(results) > 0
    assert len(results) <= 10
    scores = results.get_column("score").to_list()
    for i in range(1, len(scores)):
        assert scores[i - 1] >= scores[i]


def test_recommend_science_for_investigative():
    results = recommend(INVESTIGATIVE_PROFILE, limit=20)
    top_fields = results.head(10).get_column("cine_amplio").to_list()
    science_health = [
        f for f in top_fields
        if "Ciencias Naturales" in f or "Salud" in f or "Ingeniería" in f or "TIC" in f or "Tecnologías" in f
    ]
    assert len(science_health) > 0


def test_recommend_arts_for_artistic():
    results = recommend(ARTISTIC_PROFILE, limit=20)
    top_fields = results.head(10).get_column("cine_amplio").to_list()
    arts = [f for f in top_fields if "Arte" in f or "Ciencias Sociales" in f]
    assert len(arts) > 0


def test_recommend_department_filter():
    results = recommend(
        INVESTIGATIVE_PROFILE,
        departments=["Sucre"],
        limit=20,
    )
    for dept in results.get_column("departamento").to_list():
        assert dept == "Sucre"


def test_recommend_nivel_filter():
    results = recommend(
        INVESTIGATIVE_PROFILE,
        nivel_formacion=["Universitario"],
        limit=10,
    )
    for nivel in results.get_column("nivel_formacion").to_list():
        assert nivel == "Universitario"


def test_recommend_has_score_columns():
    results = recommend(INVESTIGATIVE_PROFILE, limit=5)
    assert "score" in results.columns
    assert "similarity" in results.columns
    assert "matching_types" in results.columns


def test_recommend_respects_limit():
    results = recommend(INVESTIGATIVE_PROFILE, limit=5)
    assert len(results) <= 5
