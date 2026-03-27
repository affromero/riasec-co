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

    ax.set_title("Perfil RIASEC del estudiante", fontsize=14, fontweight="bold", pad=20)

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
    """Show the access gap: programs per CINE field, region vs rest of country."""
    import polars as pl

    df = Programs.active()
    region_depts = ["Sucre", "Córdoba", "Bolívar"]

    region = df.filter(pl.col("departamento").is_in(region_depts))
    rest = df.filter(~pl.col("departamento").is_in(region_depts))

    short = {
        "Administración de Empresas y Derecho": "Administración\ny Derecho",
        "Ingeniería, Industria y Construcción": "Ingeniería",
        "Ciencias Sociales, Periodismo e Información": "Ciencias Sociales",
        "Salud y Bienestar": "Salud",
        "Arte y Humanidades": "Arte y Humanidades",
        "Tecnologías de la Información y la Comunicación (TIC)": "TIC",
        "Agropecuario, Silvicultura, Pesca y Veterinaria": "Agropecuario",
        "Ciencias Naturales, Matemáticas y Estadística": "Ciencias Naturales",
        "Educación": "Educación",
        "Servicios": "Servicios",
    }

    # Get all fields, sorted by national count
    nat_counts = (
        rest.group_by("cine_amplio").len()
        .sort("len", descending=True)
    )
    fields = [f for f in nat_counts.get_column("cine_amplio").to_list()
              if f in short]

    reg_map = dict(
        region.group_by("cine_amplio").len()
        .select("cine_amplio", "len").iter_rows()
    )
    rest_map = dict(
        rest.group_by("cine_amplio").len()
        .select("cine_amplio", "len").iter_rows()
    )

    labels = [short[f] for f in fields]
    reg_vals = [reg_map.get(f, 0) for f in fields]
    rest_vals = [rest_map.get(f, 0) for f in fields]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    y = np.arange(len(fields))
    h = 0.35

    bars1 = ax.barh(y - h/2, rest_vals, h,
                     label=f"Resto del país ({len(rest):,} programas)",
                     color="#3498db", alpha=0.85, edgecolor="white")
    bars2 = ax.barh(y + h/2, reg_vals, h,
                     label=f"Sucre + Córdoba + Bolívar ({len(region):,} programas)",
                     color="#e74c3c", alpha=0.85, edgecolor="white")

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel("Programas activos", fontsize=12)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{x:,.0f}"))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Add count labels on regional bars
    for bar, val in zip(bars2, reg_vals):
        ax.text(val + 30, bar.get_y() + bar.get_height() / 2,
                str(val), va="center", fontsize=9, color="#e74c3c", fontweight="bold")

    ax.legend(fontsize=10, loc="lower right")
    ax.set_title(
        "Brecha de acceso: 3 departamentos, 3.5M de personas, 6% de los programas",
        fontsize=13, fontweight="bold", pad=15
    )

    plt.tight_layout()
    fig.savefig(OUT / "regional-comparison.png", dpi=150, bbox_inches="tight",
                facecolor=BG, edgecolor="none")
    plt.close()
    print(f"  regional-comparison.png — region: {len(region):,}, rest: {len(rest):,}")
    return region_depts, len(region)


def plot_recommendations(profile, region_depts):
    """Show top recommendations as a styled table."""
    import polars as pl

    results = recommend(
        profile,
        departments=region_depts,
        nivel_formacion=["Universitario", "Tecnológico"],
        enrollment_weight=-0.3,
        virtual_boost=1.5,
        limit=10,
    )

    max_score = results.get_column("score").max()

    # Build table data
    rows_data = []
    for i, row in enumerate(results.iter_rows(named=True)):
        name = row["nombre_programa"].title()
        if len(name) > 40:
            name = name[:38] + "..."
        inst = row["nombre_institucion"].title()
        if len(inst) > 35:
            inst = inst[:33] + "..."
        dept = row["departamento"]
        field = row["cine_amplio"]
        # Shorten CINE field
        field_short = {
            "Ingeniería, Industria y Construcción": "Ingeniería",
            "Administración de Empresas y Derecho": "Administración",
            "Salud y Bienestar": "Salud",
            "Tecnologías de la Información y la Comunicación (TIC)": "TIC",
            "Ciencias Naturales, Matemáticas y Estadística": "Ciencias Nat.",
            "Ciencias Sociales, Periodismo e Información": "Ciencias Soc.",
            "Agropecuario, Silvicultura, Pesca y Veterinaria": "Agropecuario",
            "Arte y Humanidades": "Arte",
            "Educación": "Educación",
            "Servicios": "Servicios",
        }.get(field, field[:15])
        mod = "Virtual" if row["modalidad"] in ("Virtual", "A distancia") else "Presencial"
        pct = int(row["score"] / max_score * 100)
        rows_data.append([f"{i+1}", name, inst, dept, field_short, mod, f"{pct}%"])

    columns = ["#", "Programa", "Institución", "Depto.", "Campo", "Modalidad", "Match"]
    col_widths = [0.03, 0.27, 0.24, 0.10, 0.12, 0.10, 0.07]

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.axis("off")

    # Header
    header_colors = ["#2c3e50"] * len(columns)
    table = ax.table(
        cellText=rows_data,
        colLabels=columns,
        colWidths=col_widths,
        cellLoc="left",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9.5)
    table.scale(1, 1.6)

    # Style header
    for j in range(len(columns)):
        cell = table[0, j]
        cell.set_facecolor("#2c3e50")
        cell.set_text_props(color="white", fontweight="bold", fontsize=10)
        cell.set_edgecolor("#1a252f")

    # Style data rows
    for i in range(len(rows_data)):
        bg = "#f8f9fa" if i % 2 == 0 else "white"
        for j in range(len(columns)):
            cell = table[i + 1, j]
            cell.set_facecolor(bg)
            cell.set_edgecolor("#e1e4e8")
            # Color the match percentage
            if j == len(columns) - 1:
                cell.set_text_props(fontweight="bold", color="#27ae60")
            # Color virtual/presencial
            if j == len(columns) - 2:
                mod_val = rows_data[i][j]
                color = "#27ae60" if mod_val == "Virtual" else "#3498db"
                cell.set_text_props(color=color, fontweight="bold")

    ax.set_title(
        "Recomendaciones para un estudiante Investigador + Realista en Sucre/Córdoba/Bolívar",
        fontsize=12, fontweight="bold", pad=15, color=TEXT_COLOR
    )

    plt.tight_layout()
    fig.savefig(OUT / "recommendations.png", dpi=150, bbox_inches="tight",
                facecolor=BG, edgecolor="none")
    plt.close()
    print(f"  recommendations.png — {len(rows_data)} programs (table)")


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
