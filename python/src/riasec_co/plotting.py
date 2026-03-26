"""Convenience plotting for RIASEC profiles and enrollment data."""

from __future__ import annotations

from riasec_co.scoring import RIASEC_TYPES

RIASEC_COLORS = {
    "R": "#e74c3c",
    "I": "#3498db",
    "A": "#9b59b6",
    "S": "#2ecc71",
    "E": "#f39c12",
    "C": "#95a5a6",
}

RIASEC_LABELS_ES = {
    "R": "Realista",
    "I": "Investigador",
    "A": "Artístico",
    "S": "Social",
    "E": "Emprendedor",
    "C": "Convencional",
}


def plot_profile(
    profile: dict[str, float],
    *,
    title: str = "Perfil RIASEC",
    language: str = "es",
) -> "matplotlib.figure.Figure":
    """Create a radar chart of a RIASEC profile.

    Requires matplotlib (install with `pip install riasec-co[plot]`).
    """
    import matplotlib.pyplot as plt
    import numpy as np

    labels = (
        [RIASEC_LABELS_ES[t] for t in RIASEC_TYPES]
        if language == "es"
        else list(RIASEC_TYPES)
    )
    values = [profile[t] for t in RIASEC_TYPES]
    colors = [RIASEC_COLORS[t] for t in RIASEC_TYPES]

    # Close the polygon
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, len(RIASEC_TYPES), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.fill(angles, values, alpha=0.25, color="#3498db")
    ax.plot(angles, values, "o-", linewidth=2, color="#3498db")

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, size=11)
    ax.set_title(title, size=14, pad=20)
    ax.set_ylim(0, max(values) * 1.15)

    return fig
