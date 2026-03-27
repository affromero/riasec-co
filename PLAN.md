# Plan: `riasec-co` — Open-Source Bayesian Vocational Guidance Engine for Colombia

## Context

Rural Colombian students in regions like San Jorge y La Mojana lack access to career guidance. Existing tools are either US-centric (O*NET), locked behind government web forms (SNIES/HECAA), or nonexistent as open-source packages. No package on npm, PyPI, or CRAN combines vocational assessment with national higher education data — in any country.

`riasec-co` fills this gap: a Bayesian adaptive RIASEC quiz engine paired with the complete Colombian SNIES program database (17,230 active programs), published as packages for JS/TS, Python, and R. Enrollment-weighted priors surface hidden-gem programs over oversaturated fields. Everything is transparent, cited, and open.

## Prior Art: Nothing like this exists

### Registries
- **npm**: 0 results for "riasec"
- **PyPI**: 0 packages for "riasec" or "holland-code" (404)
- **CRAN**: `holland` (v0.1.2-4, Sep 2025) — RIASEC math only (congruence indices), no test delivery, no data
- **CRAN**: `mirtCAT` (101 stars) — Bayesian adaptive testing engine, domain-agnostic. Reference for our engine design, but no RIASEC item bank configured
- **GitHub**: 214 RIASEC repos (<12 stars each), 9 SNIES repos (0 stars each) — all student projects or one-off notebooks
- Colombia's "Descubre TÚ" (MinEducación) — closed government tool, no API/source

### Gap summary
| Exists | Missing |
|--------|---------|
| R `holland` — RIASEC math | Installable RIASEC package (npm/PyPI) |
| R `mirtCAT` — generic CAT engine | RIASEC item bank for adaptive testing |
| Toy RIASEC web apps | Reusable library combining assessment + data |
| O*NET career mapping (US) | Colombian SNIES mapping |

**`riasec-co` = first package combining vocational assessment + national education data, in any country.**

## Data Sources (verified, accessible)

### SNIES Program Catalog
- **Source**: HECAA portal (MinEducación Colombia) — `hecaa.mineducacion.gov.co`
- **Access method**: POST to PrimeFaces "Descargar programas" button with JSF ViewState (proven — we downloaded 7.7MB Excel with all 30,811 programs)
- **Freshness**: Live data — most recent entries from March 23, 2026
- **Schema**: 39 columns including CINE F 2013 AC (broad/specific/detailed), department, municipality, modality, tuition, accreditation
- **Active programs**: 17,230

### SNIES Enrollment Statistics
- **Source**: HECAA REST API — `/consultaspublicas/rest/poblacionales/`
- **Access method**: GET with session cookie (proven)
- **Endpoints**: `parametrizacion`, `datoscategoria`, `historico`, `mapa`
- **Data**: Enrollment counts by CINE field, department, gender, sector, level (2016–2024)
- **Use**: Bayesian prior weights — high enrollment = well-known = downweight

### IPIP RIASEC Markers
- **Source**: International Personality Item Pool (`ipip.ori.org`)
- **Items**: 48 public-domain items (8 per RIASEC type)
- **Validation**: Liao, Armstrong & Rounds (2008), Journal of Vocational Behavior
- **Spanish adaptation**: Armstrong, Allison & Rounds (2020), Electronic Journal of Research in Educational Psychology
- **License**: Public domain — no restrictions

## Architecture

### Repository Structure

```
riasec-co/
├── README.md                    # Project overview, badges, citations
├── METHODOLOGY.md               # Full scientific methodology (public)
├── LICENSE                      # MIT
├── data/
│   ├── canonical/
│   │   ├── programs.parquet     # SNIES programs (canonical format)
│   │   ├── programs.csv         # Same data as CSV (universal access)
│   │   ├── enrollment.parquet   # Enrollment stats by field/dept/year
│   │   ├── enrollment.csv
│   │   ├── items_en.json        # IPIP RIASEC items (English)
│   │   ├── items_es.json        # IPIP RIASEC items (Spanish)
│   │   └── mapping.json         # RIASEC → CINE field mapping with weights
│   └── schema/
│       ├── programs.schema.json # JSON Schema for programs
│       └── enrollment.schema.json
├── packages/
│   ├── core/                    # Framework-agnostic TS engine
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   ├── src/
│   │   │   ├── index.ts
│   │   │   ├── quiz.ts          # Bayesian adaptive quiz engine
│   │   │   ├── scoring.ts       # Dirichlet posterior updates
│   │   │   ├── recommender.ts   # Program matching with configurable priors
│   │   │   ├── items.ts         # IPIP item bank loader
│   │   │   ├── programs.ts      # SNIES program data loader
│   │   │   └── types.ts         # Shared types
│   │   └── __tests__/
│   ├── react/                   # React components (quiz, results, cards)
│   │   ├── package.json
│   │   └── src/
│   └── cli/                     # CLI for data refresh & exploration
│       ├── package.json
│       └── src/
├── python/                      # Python package
│   ├── pyproject.toml
│   ├── src/riasec_co/
│   │   ├── __init__.py
│   │   ├── quiz.py              # Bayesian engine (Python port)
│   │   ├── data.py              # Data loaders (reads canonical parquet/csv)
│   │   ├── recommender.py
│   │   └── plotting.py          # Convenience plotting (matplotlib/plotly)
│   └── tests/
├── r/                           # R package
│   ├── DESCRIPTION
│   ├── NAMESPACE
│   ├── R/
│   │   ├── data.R               # Data documentation
│   │   ├── quiz.R               # Quiz engine
│   │   └── recommend.R
│   ├── data/                    # R .rda data files (auto-generated from canonical)
│   ├── man/                     # Documentation
│   └── vignettes/               # R Markdown tutorials
├── scripts/
│   ├── update-snies.ts          # Download + parse SNIES Excel → canonical data
│   ├── update-enrollment.ts     # Fetch enrollment stats from REST API
│   ├── generate-r-data.R        # Convert canonical → R .rda format
│   └── validate-data.ts         # Schema validation
└── .github/
    └── workflows/
        ├── ci.yml               # Lint, test, type-check all packages
        ├── update-data.yml      # Monthly SNIES refresh (cron)
        ├── publish-npm.yml      # Publish @riasec-co/* to npm
        ├── publish-pypi.yml     # Publish riasec-co to PyPI
        └── publish-cran.yml     # R CMD check + CRAN submission prep
```

### Why this structure (informed by Arrow/DuckDB/Polars patterns)

Arrow, DuckDB, and Polars all ship multi-language from monorepos. For a data+logic package (no native binaries), the pattern is simpler:

- **`data/canonical/`**: Single source of truth. Parquet + CSV dual format.
- **`packages/core/`**: Zero-dependency TypeScript engine. Works in browser and Node. Uses `hyparquet` (pure JS, 0 deps) for Parquet reading.
- **`packages/react/`**: Optional. Only for React/Next.js consumers (like Hicotea).
- **`python/` and `r/`**: Separate language packages with own idioms (Python: dataclasses + polars; R: tibbles + vignettes + .rda data).
- **`scripts/`**: Data pipeline. Monthly via GitHub Action or manual `npm run update-snies`.
- **Tooling**: Makefile at root. No Turborepo/Nx needed — those solve JS-only problems.

### Data Format Decision: Parquet + CSV dual format

| Format | Size | Typed | JS | Python | R | Researchers |
|--------|------|-------|-----|--------|---|-------------|
| **Parquet** | ~800KB | Yes | `hyparquet` (pure JS, 0 deps) | `pyarrow`/`polars` | `arrow` | Good |
| **CSV** | ~4MB | No | built-in | `pandas` | `read.csv` | Excellent |
| JSON | ~8MB | No | built-in | json | jsonlite | OK |
| SQLite | ~2MB | Yes | better-sqlite3 | sqlite3 | RSQLite | Fragile cross-lang dates |

Ship both Parquet (primary, typed, compact) and CSV (universal fallback). Avoid SQLite — cross-language date type coercion is a real footgun. Researchers can open CSV in Excel/pandas/R without installing anything.

### R Package Constraints (CRAN-ready)
- CRAN limit: 5MB source tarball. Our data as `.rda` ≈ 200-800KB — fits easily.
- `LazyData: true` required (datasets load on-demand).
- Every dataset needs roxygen2 documentation in `R/data.R`.
- Auto-generate `.rda` from canonical Parquet via `data-raw/generate.R`.
- Publish to CRAN (pure data, no compiled code) + R-universe as parallel channel.

### CI/CD: Publishing
- **npm**: Fully automated. npm provenance + `NODE_AUTH_TOKEN`.
- **PyPI**: Fully automated. PyPI Trusted Publishers via OIDC — no secrets needed.
- **CRAN**: Automated up to `devtools::submit_cran()`. Maintainer email confirmation is unavoidable (CRAN policy).

## Core API Design

### TypeScript (packages/core)

```typescript
import { createQuiz, loadPrograms, recommend } from '@riasec-co/core'

// Start adaptive quiz
const quiz = createQuiz({ language: 'es', mode: 'adaptive' })

// Get first question
let question = quiz.nextQuestion()
// { id: 'I3', text: '¿Te gusta resolver rompecabezas complejos?', type: 'investigative' }

// Submit answer (1-5 Likert scale)
quiz.answer(question.id, 4)

// Check if quiz should continue (entropy-based stopping)
quiz.isComplete()  // false — posterior still uncertain
quiz.progress()    // { answered: 1, estimatedRemaining: 11, confidence: 0.32 }

// Get current posterior
quiz.profile()
// { R: 0.12, I: 0.28, A: 0.15, S: 0.18, E: 0.14, C: 0.13, entropy: 2.1 }

// After quiz completes — get recommendations
const programs = loadPrograms()  // loads from bundled data
const results = recommend({
  profile: quiz.profile(),
  programs,
  filters: { departments: ['Sucre', 'Córdoba', 'Bolívar'], active: true },
  priors: {
    enrollmentWeight: -0.3,   // downweight oversaturated fields
    regionalBoost: 1.5,       // boost programs in student's region
    virtualBoost: 1.2,        // boost distance/virtual programs
  },
  limit: 20,
})
// [{ program: 'Acuicultura', institution: '...', score: 0.87, ... }, ...]
```

### Python (python/)

```python
from riasec_co import Quiz, Programs, recommend

# Same API philosophy, Pythonic idioms
quiz = Quiz(language="es", mode="adaptive")
q = quiz.next_question()
quiz.answer(q.id, 4)

profile = quiz.profile  # property, not method
programs = Programs.load()  # returns polars DataFrame

# Researchers can also just load the data
df = Programs.load()
df.filter(pl.col("departamento") == "Sucre").group_by("cine_amplio").count()

# Plotting convenience
from riasec_co.plotting import plot_profile, plot_enrollment
plot_profile(profile)  # radar chart
plot_enrollment(department="Sucre")  # bar chart by CINE field
```

### R (r/)

```r
library(riasecco)

# Data access (R data package pattern)
data(programs)   # tibble with 17,230 rows
data(enrollment) # enrollment stats

# Quiz
quiz <- riasec_quiz(language = "es")
q <- next_question(quiz)
quiz <- answer(quiz, q$id, 4L)
profile(quiz)

# Researchers: just use the data
programs %>%
  filter(departamento == "Sucre", estado == "Activo") %>%
  count(cine_amplio, sort = TRUE)

# Vignettes ship with the package showing common analyses
```

## RIASEC → CINE Mapping

Based on verified SNIES data (11 broad fields, 37 specific fields):

| RIASEC | Primary CINE Broad Fields | Weight |
|--------|--------------------------|--------|
| **R** Realistic | Agropecuario/Silvicultura/Pesca/Veterinaria; Ingeniería/Industria/Construcción | 1.0 |
| **R** Realistic | Servicios (transporte, seguridad) | 0.5 |
| **I** Investigative | Ciencias Naturales/Matemáticas/Estadística; Salud y Bienestar | 1.0 |
| **I** Investigative | TIC; Ingeniería (research) | 0.5 |
| **A** Artistic | Arte y Humanidades | 1.0 |
| **A** Artistic | Ciencias Sociales/Periodismo/Información (comunicación, periodismo) | 0.5 |
| **S** Social | Educación; Salud y Bienestar | 1.0 |
| **S** Social | Ciencias Sociales/Periodismo/Información | 0.7 |
| **E** Enterprising | Administración de Empresas y Derecho | 1.0 |
| **E** Enterprising | Servicios | 0.5 |
| **C** Conventional | TIC | 1.0 |
| **C** Conventional | Administración (contabilidad side) | 0.7 |

This mapping lives in `data/canonical/mapping.json` and is overridable by consumers.

## Bayesian Engine Design

### Quiz (adaptive item selection)

1. **Prior**: Dirichlet(α=1,1,1,1,1,1) — uniform over 6 RIASEC types
2. **Item response model**: Each of 48 IPIP items has known loadings on RIASEC types (from validation studies). A high response on an Investigative item increases the I posterior.
3. **Posterior update**: After each answer, update Dirichlet parameters based on item loadings × response value
4. **Next question selection**: Pick the item that maximizes expected information gain (KL divergence between current posterior and expected posterior after answering)
5. **Stopping rule**: Stop when posterior entropy < threshold (configurable). Default: ~12 questions for "quick", all 48 for "full"

### Recommender (enrollment-weighted priors)

```
score(program) = similarity(student_profile, program_cine_vector)
              × prior(program)

prior(program) = base
              × (1 + enrollmentWeight × log(national_enrollment / field_enrollment))
              × (1 + regionalBoost × isInRegion)
              × (1 + virtualBoost × isVirtualOrDistance)
```

Where `enrollmentWeight` is negative (default -0.3), causing high-enrollment fields to be downweighted. The math naturally surfaces Acuicultura (low enrollment) over Derecho (high enrollment) for equal RIASEC match strength.

## Phased Implementation

### Phase 1: Data pipeline + canonical data (1 session)
- `scripts/update-snies.ts` — download HECAA Excel, parse, output Parquet + CSV
- `scripts/update-enrollment.ts` — fetch REST API enrollment data
- `data/canonical/` — programs, enrollment, items, mapping
- `data/schema/` — JSON Schema validation
- **Commit**: Data pipeline works, canonical data files generated

### Phase 2: TypeScript core engine (1 session)
- `packages/core/` — quiz, scoring, recommender, types
- Unit tests for Bayesian math, item selection, recommendation ranking
- **Commit**: `npm test` passes, engine works standalone

### Phase 3: Python package (1 session)
- `python/` — port core engine, add data loaders, plotting convenience
- `pyproject.toml` with proper metadata and dependencies
- Tests mirroring TypeScript suite
- **Commit**: `pytest` passes, `pip install -e .` works

### Phase 4: R package (1 session)
- `r/` — DESCRIPTION, data documentation, quiz functions, vignettes
- Auto-generate `.rda` from canonical data
- `R CMD check` passes
- **Commit**: R package installable, vignettes render

### Phase 5: React components + Hicotea integration (1 session)
- `packages/react/` — QuizWidget, ProfileChart, ProgramCards
- Update `fundacionhicotea` to install `@riasec-co/react` and use it on `/orientacion`
- **Commit**: Hicotea site has working interactive quiz

### Phase 6: CI/CD + publishing (1 session)
- GitHub Actions: CI, monthly SNIES refresh, npm/PyPI publish
- README with badges, installation instructions, citations
- METHODOLOGY.md with full scientific documentation

## Verification

- `npm run ci` in packages/core — lint + type-check + test
- `pytest python/` — Python test suite
- `R CMD check r/` — R package validation
- `npm run update-snies` — verify data refresh pipeline
- Manual: run quiz in browser, check recommendations for a Sucre student

## References (to cite in METHODOLOGY.md)

- Holland, J. L. (1997). Making vocational choices. Psychological Assessment Resources.
- Liao, H.-Y., Armstrong, P. I., & Rounds, J. (2008). Development and initial validation of public domain Basic Interest Markers. Journal of Vocational Behavior, 73(1), 159–183.
- Armstrong, P. I., Allison, W., & Rounds, J. (2020). Alternate Forms Public Domain RIASEC Markers. Electronic Journal of Research in Educational Psychology.
- Nye, C. D., et al. (2012). Vocational interests and performance: A quantitative summary. Perspectives on Psychological Science.
- Nye, C. D., et al. (2020). Interest congruence and job satisfaction: A meta-analysis. Journal of Vocational Behavior.
- van der Linden, W. J., & Hambleton, R. K. (2018). Handbook of Item Response Theory. CRC Press.
- SNIES, Ministerio de Educación Nacional de Colombia. https://hecaa.mineducacion.gov.co/consultaspublicas/programas
- IPIP: International Personality Item Pool. https://ipip.ori.org/
