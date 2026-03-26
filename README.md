# riasec-co

Bayesian adaptive RIASEC vocational guidance engine for Colombia.

Combines a 48-item [IPIP](https://ipip.ori.org/) quiz engine with the complete [SNIES](https://hecaa.mineducacion.gov.co/consultaspublicas/programas) program catalog (17,230 active programs). Enrollment-weighted priors surface hidden-gem programs over oversaturated fields. Available as packages for **TypeScript/JavaScript**, **Python**, and **R**.

## Install

### TypeScript / JavaScript

```bash
npm install @riasec-co/core
# React components (optional):
npm install @riasec-co/react
```

### Python

```bash
pip install riasec-co
```

### R

```r
# install.packages("riasecco")  # CRAN (coming soon)
# Or from GitHub:
# remotes::install_github("afromero/riasec-co", subdir = "r")
```

## Quick Start

### TypeScript

```typescript
import { createQuiz, loadPrograms, recommend } from '@riasec-co/core'

const quiz = createQuiz({ language: 'es', mode: 'adaptive' })

let q = quiz.nextQuestion()
quiz.answer(q.id, 4) // 1-5 Likert scale

// After quiz completes:
const programs = loadPrograms()
const results = recommend({
  profile: quiz.profile(),
  programs,
  filters: { departments: ['Sucre', 'Córdoba'], active: true },
  priors: { enrollmentWeight: -0.3, virtualBoost: 1.2 },
  limit: 20,
})
```

### Python

```python
from riasec_co import Quiz, Programs, recommend

quiz = Quiz(language="es", mode="adaptive")
q = quiz.next_question()
quiz.answer(q.id, 4)

results = recommend(
    quiz.profile,
    departments=["Sucre", "Córdoba"],
    limit=20,
)
# Returns a Polars DataFrame
```

### R

```r
library(riasecco)

data(programs)  # 30,809 programs as a data.frame
data(items_es)  # 48 IPIP items in Spanish

quiz <- create_quiz(language = "es")
q <- next_question(quiz)
answer(quiz, q$id, 4L)

results <- recommend(profile(quiz), departments = "Sucre")
```

## How It Works

1. **Dirichlet prior**: Starts with uniform belief over 6 RIASEC types
2. **Adaptive item selection**: Picks the question that maximizes expected information gain (KL divergence)
3. **Bayesian update**: Each answer updates the Dirichlet posterior
4. **Entropy-based stopping**: Stops when the profile is confident enough (~12 questions in adaptive mode)
5. **Program matching**: Cosine similarity between student profile and CINE field vectors
6. **Enrollment-weighted priors**: Downweights oversaturated fields, boosts regional and virtual programs

## Data Sources

| Source | Description | Access |
|--------|-------------|--------|
| [SNIES/HECAA](https://hecaa.mineducacion.gov.co/consultaspublicas/programas) | 30,809 higher education programs (17,230 active) | Public, downloaded via HECAA portal |
| [IPIP](https://ipip.ori.org/) | 48 public-domain RIASEC interest markers | Public domain |
| RIASEC→CINE Mapping | Expert mapping from Holland types to CINE F 2013 AC fields | Original, included in package |

## Repository Structure

```
riasec-co/
├── data/canonical/        # Canonical data (CSV + JSON)
├── packages/core/         # TypeScript engine (zero-dep)
├── packages/react/        # React components
├── python/                # Python package (Polars)
├── r/                     # R package (CRAN-ready)
├── scripts/               # Data pipeline
└── .github/workflows/     # CI/CD
```

## Development

```bash
# Data pipeline
npm install
npm run update-snies    # Parse SNIES Excel → CSV
npm run validate        # Validate all data files

# TypeScript
cd packages/core && npm install && npm run ci

# Python
cd python && uv venv && source .venv/bin/activate
uv pip install -e ".[dev]" && pytest

# R
Rscript r/data-raw/generate.R
R CMD check r/
```

## References

- Holland, J. L. (1997). *Making vocational choices*. Psychological Assessment Resources.
- Liao, H.-Y., Armstrong, P. I., & Rounds, J. (2008). Development and initial validation of public domain Basic Interest Markers. *Journal of Vocational Behavior*, 73(1), 159-183.
- Armstrong, P. I., Allison, W., & Rounds, J. (2020). Alternate Forms Public Domain RIASEC Markers. *Electronic Journal of Research in Educational Psychology*.
- SNIES, Ministerio de Educacion Nacional de Colombia. https://hecaa.mineducacion.gov.co/consultaspublicas/programas
- IPIP: International Personality Item Pool. https://ipip.ori.org/

## License

MIT
