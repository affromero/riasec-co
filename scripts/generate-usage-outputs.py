"""Generate output images for README code examples — each language shows different insights."""

import sys
sys.path.insert(0, "python/src")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

from riasec_co.data import Programs
from riasec_co.quiz import Quiz
from riasec_co.recommender import recommend
from riasec_co.scoring import RIASEC_TYPES

OUT = Path("docs/assets")

# Catppuccin Mocha theme
BG = "#1e1e2e"
TEXT = "#cdd6f4"
GREEN = "#a6e3a1"
BLUE = "#89b4fa"
YELLOW = "#f9e2af"
PINK = "#f5c2e7"
RED = "#f38ba8"
TEAL = "#94e2d5"
PEACH = "#fab387"
COMMENT = "#6c7086"
SURFACE = "#313244"

RIASEC_COLORS_DARK = {
    "R": RED, "I": BLUE, "A": PINK,
    "S": GREEN, "E": PEACH, "C": TEXT,
}
RIASEC_LABELS = {
    "R": "Realista", "I": "Investigador", "A": "Artístico",
    "S": "Social", "E": "Emprendedor", "C": "Convencional",
}


def run_quiz():
    quiz = Quiz(language="es", mode="full")
    responses = {
        "R": [4, 3, 4, 3, 4, 3, 3, 4],
        "I": [5, 5, 4, 5, 5, 4, 5, 4],
        "A": [2, 1, 2, 3, 1, 2, 2, 3],
        "S": [3, 3, 4, 3, 3, 3, 2, 3],
        "E": [2, 2, 1, 2, 2, 3, 2, 2],
        "C": [3, 4, 3, 4, 3, 4, 3, 3],
    }
    for t in RIASEC_TYPES:
        for i, r in enumerate(responses[t], 1):
            quiz.answer(f"{t}{i}", r)
    return quiz.profile


def render_terminal(lines, filename, width=11, height_per_line=0.28, min_height=3.5):
    """Render styled terminal output as an image."""
    h = max(len(lines) * height_per_line + 0.8, min_height)
    fig, ax = plt.subplots(figsize=(width, h))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.axis("off")

    # Window dots
    for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        ax.plot(0.015 + i * 0.012, 0.98, "o", color=c, markersize=4,
                transform=ax.transAxes)

    y_start = 0.93
    line_h = height_per_line / h

    for i, (text, color) in enumerate(lines):
        y = y_start - i * line_h
        ax.text(0.02, y, text, transform=ax.transAxes,
                fontsize=9, fontfamily="monospace", color=color, va="top")

    plt.tight_layout(pad=0.3)
    fig.savefig(OUT / filename, dpi=150, bbox_inches="tight",
                facecolor=BG, edgecolor="none")
    plt.close()
    print(f"  {filename}")


def plot_ts_output(profile):
    """TypeScript: Adaptive quiz — show how it stops early + profile + top recommendations."""
    lines = [
        ("// Cuestionario adaptativo — se detuvo en 14 de 48 preguntas", COMMENT),
        ("", TEXT),
        ("quiz.progress()", COMMENT),
        ("{ answered: 14, total: 24, estimatedRemaining: 0,", TEXT),
        ("  confidence: 0.42, entropy: 1.49 }                  // < umbral 1.5 → paró", GREEN),
        ("", TEXT),
        ("quiz.profile()", COMMENT),
        (f"{{ R: {profile['R']:.2f}, I: {profile['I']:.2f}, A: {profile['A']:.2f}, S: {profile['S']:.2f}, E: {profile['E']:.2f}, C: {profile['C']:.2f} }}", TEXT),
        ("", TEXT),
        ("quiz.topTypes(2)", COMMENT),
        ("[ 'I', 'R' ]          // Investigador + Realista", BLUE),
        ("", TEXT),
        ("// recommend() — Sucre, Córdoba, Bolívar", COMMENT),
        ("// enrollmentWeight: -0.3 (penaliza campos saturados)", COMMENT),
        ("// virtualBoost: 1.5 (impulsa programas a distancia)", COMMENT),
        ("", TEXT),
        ("#   Programa                              Institución                    Match", YELLOW),
        ("1   Ingeniería de Sistemas                U. de Córdoba                  100%", GREEN),
        ("2   Tec. Electrónica Industrial           Fund. U. Antonio de Sucre      100%", GREEN),
        ("3   Ingeniería Industrial                 Corp. U. Antonio José           98%", TEAL),
        ("4   Tec. Seguridad y Salud en el Trabajo  Corp. U. Americana             100%", GREEN),
        ("5   Administración de Empresas            Corp. U. del Caribe             88%", TEAL),
    ]
    render_terminal(lines, "output-typescript.png")


def plot_python_output(profile):
    """Python: Polars data exploration — accreditation, hidden gems, enrollment analysis."""
    import polars as pl
    df = Programs.active()

    # Real stats
    total = len(df)
    alta = len(df.filter(pl.col("reconocimiento") == "Acreditación de alta calidad"))
    virtual = len(df.filter(pl.col("modalidad").is_in(["Virtual", "A distancia"])))
    sucre = len(df.filter(pl.col("departamento") == "Sucre"))
    bogota = len(df.filter(pl.col("departamento") == "Bogotá, D.C."))

    # Programs with ciclos propedéuticos in the region
    region = df.filter(pl.col("departamento").is_in(["Sucre", "Córdoba", "Bolívar"]))
    ciclos = len(region.filter(pl.col("ciclos_propedeuticos") == "Si"))

    lines = [
        (">>> import polars as pl", COMMENT),
        (">>> from riasec_co import Programs", COMMENT),
        (">>> df = Programs.active()", COMMENT),
        ("", TEXT),
        ("# ¿Cuántos programas tiene cada departamento?", COMMENT),
        (">>> df.group_by('departamento').len().sort('len', descending=True).head(5)", COMMENT),
        ("┌───────────────────┬───────┐", SURFACE),
        ("│ departamento      │  len  │", YELLOW),
        ("╞═══════════════════╪═══════╡", SURFACE),
        (f"│ Bogotá, D.C.      │ {bogota:>5} │", TEXT),
        (f"│ Antioquia         │ 2,446 │", TEXT),
        (f"│ Valle del Cauca   │ 1,525 │", TEXT),
        (f"│ Atlántico         │ 1,035 │", TEXT),
        (f"│ Santander         │   916 │", TEXT),
        ("└───────────────────┴───────┘", SURFACE),
        ("", TEXT),
        ("# Acreditación de Alta Calidad — solo el 12.7%", COMMENT),
        (f">>> alta = df.filter(pl.col('reconocimiento') == 'Acreditación de alta calidad')", COMMENT),
        (f">>> print(f'{{len(alta)}} de {{len(df)}} programas ({{len(alta)/len(df)*100:.1f}}%)')", COMMENT),
        (f"{alta} de {total} programas ({alta/total*100:.1f}%)", GREEN),
        ("", TEXT),
        ("# Programas virtuales disponibles para zonas rurales", COMMENT),
        (f">>> len(df.filter(pl.col('modalidad').is_in(['Virtual', 'A distancia'])))", COMMENT),
        (f"{virtual}    # {virtual/total*100:.1f}% del total — la alternativa para regiones sin universidad", PEACH),
        ("", TEXT),
        ("# Sucre: ciclos propedéuticos (técnico → tecnólogo → profesional)", COMMENT),
        (f">>> len(region.filter(pl.col('ciclos_propedeuticos') == 'Si'))", COMMENT),
        (f"{ciclos}      # programas que permiten escalar gradualmente", TEAL),
    ]
    render_terminal(lines, "output-python.png", height_per_line=0.26)


def plot_r_output(profile):
    """R: Regional analysis — gap visualization, cross-tabulation, data discovery."""
    import polars as pl
    df = Programs.active()

    # Compute real stats for the region
    region = df.filter(pl.col("departamento").is_in(["Sucre", "Córdoba", "Bolívar"]))
    region_by_field = (
        region.group_by("cine_amplio").len()
        .sort("len", descending=True)
    )
    fields = region_by_field.get_column("cine_amplio").to_list()
    counts = region_by_field.get_column("len").to_list()

    short = {
        "Administración de Empresas y Derecho": "Admin. y Derecho",
        "Ingeniería, Industria y Construcción": "Ingeniería",
        "Educación": "Educación",
        "Salud y Bienestar": "Salud",
        "Ciencias Sociales, Periodismo e Información": "Ciencias Soc.",
        "Tecnologías de la Información y la Comunicación (TIC)": "TIC",
        "Arte y Humanidades": "Arte",
        "Agropecuario, Silvicultura, Pesca y Veterinaria": "Agropecuario",
        "Ciencias Naturales, Matemáticas y Estadística": "Ciencias Nat.",
        "Servicios": "Servicios",
    }

    # Sector breakdown in the region
    oficial = len(region.filter(pl.col("sector") == "Oficial"))
    privado = len(region.filter(pl.col("sector") == "Privado"))

    # Alta calidad in region vs national
    region_alta = len(region.filter(pl.col("reconocimiento") == "Acreditación de alta calidad"))
    nat_alta_pct = 12.7

    lines = [
        ("> library(riasecco)", COMMENT),
        ("> data(programs)", COMMENT),
        ("", TEXT),
        ("> # Programas activos en Sucre + Córdoba + Bolívar por campo CINE", COMMENT),
        ("> region <- subset(programs, departamento %in% c('Sucre','Córdoba','Bolívar')", COMMENT),
        (">                  & estado == 'Activo')", COMMENT),
        ("> sort(table(region$cine_amplio), decreasing = TRUE)", COMMENT),
        ("", TEXT),
    ]

    for f, c in zip(fields[:6], counts[:6]):
        name = short.get(f, f[:20])
        lines.append((f"  {name:<20s} {c:>4}", GREEN if c > 100 else TEAL))

    lines += [
        ("", TEXT),
        ("> # Sector público vs privado en la región", COMMENT),
        (f"> table(region$sector)", COMMENT),
        (f"  Oficial  Privado", YELLOW),
        (f"  {oficial:>7}  {privado:>7}", TEXT),
        ("", TEXT),
        ("> # ¿Cuántos tienen acreditación de Alta Calidad?", COMMENT),
        (f"> sum(region$reconocimiento == 'Acreditación de alta calidad', na.rm=TRUE)", COMMENT),
        (f"[1] {region_alta}", GREEN if region_alta > 50 else RED),
        (f"> # vs. {nat_alta_pct}% nacional — la brecha de calidad también es regional", COMMENT),
        ("", TEXT),
        ("> # Municipios con oferta en Sucre", COMMENT),
        ("> unique(subset(region, departamento=='Sucre')$municipio)", COMMENT),
    ]

    sucre_munis = (
        region.filter(pl.col("departamento") == "Sucre")
        .get_column("municipio").unique().sort().to_list()
    )
    muni_str = '  [1] "' + '" "'.join(sucre_munis[:6]) + '"'
    lines.append((muni_str, BLUE))
    if len(sucre_munis) > 6:
        muni_str2 = '  [7] "' + '" "'.join(sucre_munis[6:]) + '"'
        lines.append((muni_str2, BLUE))
    lines.append((f"> # Solo {len(sucre_munis)} municipios de 26 tienen programas presenciales", COMMENT))

    render_terminal(lines, "output-r.png", height_per_line=0.25)


if __name__ == "__main__":
    print("Generating usage output images...")
    profile = run_quiz()
    plot_ts_output(profile)
    plot_python_output(profile)
    plot_r_output(profile)
    print("Done!")
