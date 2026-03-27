"""Generate showcase plots for README from real SNIES + quiz data."""

import sys
sys.path.insert(0, "python/src")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from pathlib import Path

from riasec_co.data import Programs
from riasec_co.quiz import Quiz
from riasec_co.recommender import recommend
from riasec_co.scoring import RIASEC_TYPES

OUT = Path("docs/assets")
OUT.mkdir(parents=True, exist_ok=True)

# --- Colors ---
RIASEC_COLORS = {
    "R": "#e74c3c", "I": "#3498db", "A": "#9b59b6",
    "S": "#2ecc71", "E": "#f39c12", "C": "#7f8c8d",
}
RIASEC_LABELS = {
    "R": "Realista", "I": "Investigador", "A": "Artístico",
    "S": "Social", "E": "Emprendedor", "C": "Convencional",
}
BG = "#fafbfc"
GRID_COLOR = "#e1e4e8"
TEXT_COLOR = "#24292e"
ACCENT = "#0366d6"


def setup_style():
    plt.rcParams.update({
        "figure.facecolor": BG,
        "axes.facecolor": BG,
        "axes.edgecolor": GRID_COLOR,
        "axes.labelcolor": TEXT_COLOR,
        "text.color": TEXT_COLOR,
        "xtick.color": TEXT_COLOR,
        "ytick.color": TEXT_COLOR,
        "grid.color": GRID_COLOR,
        "font.family": "sans-serif",
        "font.size": 11,
    })


def plot_radar_profile():
    """Generate a RIASEC radar chart from a simulated quiz."""
    # Simulate a student with strong Investigative + moderate Realistic profile
    quiz = Quiz(language="es", mode="full")
    responses = {
        "R": [4, 3, 4, 3, 4, 3, 3, 4],  # moderate Realistic
        "I": [5, 5, 4, 5, 5, 4, 5, 4],  # strong Investigative
        "A": [2, 1, 2, 3, 1, 2, 2, 3],  # low Artistic
        "S": [3, 3, 4, 3, 3, 3, 2, 3],  # moderate Social
        "E": [2, 2, 1, 2, 2, 3, 2, 2],  # low Enterprising
        "C": [3, 4, 3, 4, 3, 4, 3, 3],  # moderate Conventional
    }
    for t in RIASEC_TYPES:
        for i, r in enumerate(responses[t], 1):
            quiz.answer(f"{t}{i}", r)

    profile = quiz.profile

    labels = [RIASEC_LABELS[t] for t in RIASEC_TYPES]
    values = [profile[t] for t in RIASEC_TYPES]
    colors = [RIASEC_COLORS[t] for t in RIASEC_TYPES]

    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, 6, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    # Grid
    for r in [0.05, 0.10, 0.15, 0.20, 0.25]:
        ax.plot(angles, [r] * 7, color=GRID_COLOR, linewidth=0.5, linestyle="-")

    # Fill + line
    ax.fill(angles, values, alpha=0.2, color="#3498db")
    ax.plot(angles, values, "o-", linewidth=2.5, color="#3498db", markersize=7)

    # Points with type colors
    for i, t in enumerate(RIASEC_TYPES):
        ax.plot(angles[i], values[i], "o", color=colors[i], markersize=10, zorder=5)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, size=12, fontweight="bold")
    ax.set_ylim(0, max(values) * 1.15)
    ax.set_yticklabels([])
    ax.spines["polar"].set_visible(False)
    ax.grid(False)

    # Value annotations
    for i, t in enumerate(RIASEC_TYPES):
        pct = f"{values[i]*100:.0f}%"
        angle = angles[i]
        r_offset = values[i] + max(values) * 0.08
        ax.text(angle, r_offset, pct, ha="center", va="center",
                fontsize=10, fontweight="bold", color=colors[i])

    plt.tight_layout()
    fig.savefig(OUT / "profile-radar.png", dpi=150, bbox_inches="tight",
                facecolor=BG, edgecolor="none")
    plt.close()
    print(f"  profile-radar.png — profile: { {t: f'{profile[t]:.1%}' for t in RIASEC_TYPES} }")
    return profile


def plot_cine_distribution():
    """Bar chart of active programs by CINE broad field."""
    df = Programs.active()
    counts = (
        df.group_by("cine_amplio")
        .len()
        .sort("len", descending=True)
    )
    fields = counts.get_column("cine_amplio").to_list()
    values = counts.get_column("len").to_list()

    # Shorten long names
    short = {
        "Administración de Empresas y Derecho": "Administración\ny Derecho",
        "Ingeniería, Industria y Construcción": "Ingeniería",
        "Ciencias Sociales, Periodismo e Información": "Ciencias\nSociales",
        "Salud y Bienestar": "Salud",
        "Arte y Humanidades": "Arte y\nHumanidades",
        "Tecnologías de la Información y la Comunicación (TIC)": "TIC",
        "Agropecuario, Silvicultura, Pesca y Veterinaria": "Agropecuario",
        "Ciencias Naturales, Matemáticas y Estadística": "Ciencias\nNaturales",
        "Educación": "Educación",
        "Servicios": "Servicios",
        "Programas y certificaciones genéricos": "Genéricos",
    }
    labels = [short.get(f, f[:20]) for f in fields]

    fig, ax = plt.subplots(figsize=(10, 5))
    colors_list = ["#2ecc71", "#3498db", "#e74c3c", "#9b59b6", "#f39c12",
                   "#1abc9c", "#e67e22", "#34495e", "#16a085", "#c0392b", "#7f8c8d"]
    bars = ax.barh(range(len(values)), values, color=colors_list[:len(values)],
                   edgecolor="white", linewidth=0.5)

    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=11)
    ax.invert_yaxis()
    ax.set_xlabel("Programas activos", fontsize=12)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{x:,.0f}"))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Value labels
    for bar, val in zip(bars, values):
        ax.text(val + 50, bar.get_y() + bar.get_height() / 2,
                f"{val:,}", va="center", fontsize=10, color=TEXT_COLOR)

    total = sum(values)
    ax.set_title(f"17,230 programas activos por campo CINE", fontsize=14, fontweight="bold", pad=15)

    plt.tight_layout()
    fig.savefig(OUT / "cine-distribution.png", dpi=150, bbox_inches="tight",
                facecolor=BG, edgecolor="none")
    plt.close()
    print(f"  cine-distribution.png — {len(fields)} fields, {total:,} total")


def plot_regional_comparison():
    """Programs in San Jorge y La Mojana region vs national."""
    df = Programs.active()
    region_depts = ["Sucre", "Córdoba", "Bolívar"]

    region = df.filter(
        df.get_column("departamento").is_in(region_depts)
    )
    national = df

    # Count by nivel_formacion
    niveles = ["Universitario", "Tecnológico", "Especialización universitaria",
               "Maestría", "Formación técnica profesional", "Doctorado"]

    region_counts = {}
    national_counts = {}
    for n in niveles:
        region_counts[n] = len(region.filter(region.get_column("nivel_formacion") == n))
        national_counts[n] = len(national.filter(national.get_column("nivel_formacion") == n))

    # Normalize to percentages
    region_total = sum(region_counts.values())
    national_total = sum(national_counts.values())

    short_niveles = {
        "Universitario": "Universitario",
        "Tecnológico": "Tecnológico",
        "Especialización universitaria": "Especialización",
        "Maestría": "Maestría",
        "Formación técnica profesional": "Técnico\nprofesional",
        "Doctorado": "Doctorado",
    }

    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(niveles))
    w = 0.35

    r_pcts = [region_counts[n] / region_total * 100 for n in niveles]
    n_pcts = [national_counts[n] / national_total * 100 for n in niveles]

    bars1 = ax.bar(x - w/2, n_pcts, w, label=f"Nacional ({national_total:,})",
                   color="#3498db", alpha=0.85, edgecolor="white")
    bars2 = ax.bar(x + w/2, r_pcts, w,
                   label=f"Sucre + Córdoba + Bolívar ({region_total:,})",
                   color="#e74c3c", alpha=0.85, edgecolor="white")

    ax.set_xticks(x)
    ax.set_xticklabels([short_niveles[n] for n in niveles], fontsize=10)
    ax.set_ylabel("% de programas activos", fontsize=12)
    ax.set_title("Distribución por nivel de formación: región vs. nacional",
                 fontsize=14, fontweight="bold", pad=15)
    ax.legend(fontsize=11, loc="upper right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{x:.0f}%"))

    plt.tight_layout()
    fig.savefig(OUT / "regional-comparison.png", dpi=150, bbox_inches="tight",
                facecolor=BG, edgecolor="none")
    plt.close()
    print(f"  regional-comparison.png — region: {region_total:,}, national: {national_total:,}")
    return region_depts, region_total


def plot_recommendations(profile, region_depts):
    """Show top recommendations as a horizontal bar chart."""
    import polars as pl

    results = recommend(
        profile,
        departments=region_depts,
        nivel_formacion=["Universitario", "Tecnológico"],
        enrollment_weight=-0.3,
        virtual_boost=1.5,
        limit=10,
    )

    names = results.get_column("nombre_programa").to_list()
    scores = results.get_column("score").to_list()
    institutions = results.get_column("nombre_institucion").to_list()
    modalities = results.get_column("modalidad").to_list()

    # Shorten names
    short_names = []
    for n, inst in zip(names, institutions):
        short_inst = inst[:35] + "..." if len(inst) > 38 else inst
        label = f"{n}\n{short_inst}"
        short_names.append(label)

    fig, ax = plt.subplots(figsize=(10, 6))

    colors = ["#2ecc71" if m in ("Virtual", "A distancia") else "#3498db"
              for m in modalities]

    bars = ax.barh(range(len(scores)), scores, color=colors,
                   edgecolor="white", linewidth=0.5)
    ax.set_yticks(range(len(short_names)))
    ax.set_yticklabels(short_names, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Puntaje de coincidencia", fontsize=12)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#3498db", label="Presencial"),
        Patch(facecolor="#2ecc71", label="Virtual / A distancia"),
    ]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=10)

    ax.set_title("Top 10 programas recomendados — Sucre, Córdoba, Bolívar\n"
                 "Perfil: Investigador + Realista | Peso matrícula: -0.3 | Boost virtual: 1.5×",
                 fontsize=12, fontweight="bold", pad=15)

    plt.tight_layout()
    fig.savefig(OUT / "recommendations.png", dpi=150, bbox_inches="tight",
                facecolor=BG, edgecolor="none")
    plt.close()
    print(f"  recommendations.png — {len(scores)} programs")


def plot_adaptive_convergence():
    """Show how the adaptive quiz converges on a profile."""
    quiz = Quiz(language="es", mode="adaptive", min_questions=6, entropy_threshold=1.5)

    entropies = []
    profiles_over_time = {t: [] for t in RIASEC_TYPES}

    # Simulate a student answering
    responses_by_type = {"R": 4, "I": 5, "A": 1, "S": 3, "E": 2, "C": 3}

    count = 0
    while not quiz.is_complete and count < 30:
        q = quiz.next_question()
        if q is None:
            break
        quiz.answer(q.id, responses_by_type.get(q.type, 3))
        count += 1

        prof = quiz.profile
        for t in RIASEC_TYPES:
            profiles_over_time[t].append(prof[t])
        entropies.append(quiz.alpha.entropy)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

    # Left: Profile convergence
    x = range(1, count + 1)
    for t in RIASEC_TYPES:
        ax1.plot(x, [v * 100 for v in profiles_over_time[t]],
                 color=RIASEC_COLORS[t], linewidth=2, label=RIASEC_LABELS[t])
    ax1.set_xlabel("Preguntas respondidas", fontsize=11)
    ax1.set_ylabel("Probabilidad (%)", fontsize=11)
    ax1.set_title("Convergencia del perfil RIASEC", fontsize=13, fontweight="bold")
    ax1.legend(fontsize=9, ncol=2, loc="upper right")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.set_xlim(1, count)

    # Right: Entropy decay
    ax2.plot(x, entropies, color=ACCENT, linewidth=2.5, marker="o", markersize=4)
    ax2.axhline(y=1.5, color="#e74c3c", linestyle="--", linewidth=1.5,
                label="Umbral de parada (1.5 bits)")
    ax2.fill_between(x, entropies, alpha=0.1, color=ACCENT)
    ax2.set_xlabel("Preguntas respondidas", fontsize=11)
    ax2.set_ylabel("Entropía (bits)", fontsize=11)
    ax2.set_title("Reducción de incertidumbre", fontsize=13, fontweight="bold")
    ax2.legend(fontsize=10)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.set_xlim(1, count)
    ax2.set_ylim(0, 2.7)

    plt.tight_layout()
    fig.savefig(OUT / "adaptive-convergence.png", dpi=150, bbox_inches="tight",
                facecolor=BG, edgecolor="none")
    plt.close()
    print(f"  adaptive-convergence.png — {count} questions, final entropy: {entropies[-1]:.2f}")


def print_stats():
    """Print key stats for the README."""
    df = Programs.load()
    active = Programs.active()

    print("\n=== Key Stats ===")
    print(f"  Total programs: {len(df):,}")
    print(f"  Active programs: {len(active):,}")
    print(f"  Departments: {active.get_column('departamento').n_unique()}")
    print(f"  CINE broad fields: {active.get_column('cine_amplio').n_unique()}")
    print(f"  Institutions: {active.get_column('nombre_institucion').n_unique()}")

    # Virtual/distance
    virtual = active.filter(
        active.get_column("modalidad").is_in(["Virtual", "A distancia"])
    )
    print(f"  Virtual/distance: {len(virtual):,} ({len(virtual)/len(active)*100:.1f}%)")

    # Public vs private
    oficial = active.filter(active.get_column("sector") == "Oficial")
    privado = active.filter(active.get_column("sector") == "Privado")
    print(f"  Public (oficial): {len(oficial):,} ({len(oficial)/len(active)*100:.1f}%)")
    print(f"  Private: {len(privado):,} ({len(privado)/len(active)*100:.1f}%)")

    # San Jorge region
    region = active.filter(
        active.get_column("departamento").is_in(["Sucre", "Córdoba", "Bolívar"])
    )
    print(f"  Sucre+Córdoba+Bolívar: {len(region):,} programs")


if __name__ == "__main__":
    setup_style()
    print("Generating showcase plots...")
    profile = plot_radar_profile()
    plot_cine_distribution()
    region_depts, _ = plot_regional_comparison()
    plot_recommendations(profile, region_depts)
    plot_adaptive_convergence()
    print_stats()
    print("\nDone! Images saved to docs/assets/")
