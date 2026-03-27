"""Tests for Dirichlet scoring."""

import math

import pytest

from riasec_co.scoring import (
    DirichletAlpha,
    cosine_similarity,
    kl_divergence,
    expected_info_gain,
    RIASEC_TYPES,
    MAX_ENTROPY,
)


def test_uniform_prior():
    alpha = DirichletAlpha()
    for t in RIASEC_TYPES:
        assert alpha[t] == 1.0


def test_update_positive_keyed():
    alpha = DirichletAlpha()
    updated = alpha.update("I", 5, "+")
    assert updated.I == 2.0  # 1 + (5-1)/4
    assert updated.R == 1.0  # unchanged


def test_update_negative_keyed():
    alpha = DirichletAlpha()
    updated = alpha.update("I", 1, "-")
    # keyed "-", response 1 → (5-1)/4 = 1.0
    assert updated.I == 2.0


def test_posterior_mean_uniform():
    alpha = DirichletAlpha()
    mean = alpha.posterior_mean()
    for t in RIASEC_TYPES:
        assert abs(mean[t] - 1 / 6) < 1e-10


def test_posterior_mean_sums_to_one():
    alpha = DirichletAlpha().update("I", 5, "+").update("A", 4, "+")
    mean = alpha.posterior_mean()
    assert abs(sum(mean.values()) - 1.0) < 1e-10


def test_posterior_mean_favors_updated_type():
    alpha = DirichletAlpha().update("I", 5, "+").update("I", 5, "+")
    mean = alpha.posterior_mean()
    for t in RIASEC_TYPES:
        if t != "I":
            assert mean["I"] > mean[t]


def test_entropy_maximal_for_uniform():
    assert abs(DirichletAlpha().entropy - MAX_ENTROPY) < 1e-10


def test_entropy_decreases_with_evidence():
    prior = DirichletAlpha()
    updated = prior.update("I", 5, "+")
    assert updated.entropy < prior.entropy


def test_confidence_zero_for_uniform():
    assert abs(DirichletAlpha().confidence) < 1e-10


def test_confidence_increases_with_evidence():
    prior = DirichletAlpha()
    updated = prior.update("E", 5, "+")
    assert updated.confidence > prior.confidence


def test_confidence_in_range():
    alpha = DirichletAlpha()
    for _ in range(10):
        alpha = alpha.update("S", 5, "+")
        assert 0 <= alpha.confidence <= 1


def test_cosine_similarity_identical():
    alpha = DirichletAlpha().update("I", 5, "+")
    profile = alpha.posterior_mean()
    assert abs(cosine_similarity(profile, profile) - 1.0) < 1e-10


def test_cosine_similarity_different():
    a = DirichletAlpha().update("R", 5, "+").posterior_mean()
    b = DirichletAlpha().update("A", 5, "+").posterior_mean()
    assert cosine_similarity(a, b) < 1.0


def test_cosine_similarity_orthogonal():
    a = {t: 0.0 for t in RIASEC_TYPES}
    b = {t: 0.0 for t in RIASEC_TYPES}
    a["R"] = 1.0
    b["C"] = 1.0
    assert cosine_similarity(a, b) == 0.0


def test_kl_divergence_zero_for_identical():
    p = DirichletAlpha().posterior_mean()
    assert abs(kl_divergence(p, p)) < 1e-10


def test_kl_divergence_positive_for_different():
    p = DirichletAlpha().update("I", 5, "+").posterior_mean()
    q = DirichletAlpha().posterior_mean()
    assert kl_divergence(p, q) > 0


def test_expected_info_gain_higher_for_uncertain_types():
    alpha = DirichletAlpha().update("I", 5, "+").update("I", 5, "+")
    gain_r = expected_info_gain(alpha, "R")
    gain_i = expected_info_gain(alpha, "I")
    assert gain_r > gain_i
