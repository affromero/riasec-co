# riasec-co

**Connects each student's vocational profile with Colombia's 17,230 active SNIES programs.**

Bayesian adaptive RIASEC engine with the complete SNIES catalog — 33 departments, 297 institutions. Zero runtime dependencies.

[![npm](https://img.shields.io/npm/v/riasec-co)](https://www.npmjs.com/package/riasec-co)
[![CI](https://github.com/affromero/riasec-co/actions/workflows/ci.yml/badge.svg)](https://github.com/affromero/riasec-co/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

## Install

```bash
npm install riasec-co
```

## Quick Start

```typescript
import { createQuiz, loadPrograms, recommend } from 'riasec-co'

// 1. Run adaptive quiz (~12 questions instead of 48)
const quiz = createQuiz({ language: 'es', mode: 'adaptive' })
while (!quiz.isComplete()) {
  const q = quiz.nextQuestion()!
  const response = await askUser(q.text) // your UI
  quiz.answer(q.id, response)
}

console.log(quiz.profile())
// { R: 0.19, I: 0.27, A: 0.10, S: 0.16, E: 0.10, C: 0.18 }
console.log(quiz.topTypes(2)) // ['I', 'R']

// 2. Get program recommendations
const results = recommend({
  profile: quiz.profile(),
  programs: loadPrograms(),
  filters: { departments: ['Sucre', 'Cordoba', 'Bolivar'], active: true },
  priors: { enrollmentWeight: -0.3, virtualBoost: 1.5 },
  limit: 10,
})

results.forEach((r, i) =>
  console.log(`${i + 1}. ${r.program.nombre_programa} (${r.score.toFixed(2)})`)
)
```

## API

### Quiz

| Function | Description |
|----------|-------------|
| `createQuiz(config?)` | Create a quiz instance (`language`: `"es"` or `"en"`, `mode`: `"adaptive"` or `"full"`) |
| `quiz.nextQuestion()` | Next item (or `null` if complete) |
| `quiz.answer(id, response)` | Record a Likert response (1-5) |
| `quiz.isComplete()` | Whether the quiz has enough information to stop |
| `quiz.profile()` | Current RIASEC profile (`RIASECProfile`) |
| `quiz.topTypes(n?)` | Top N types sorted by probability |
| `quiz.progress()` | `{ answered, total, estimatedRemaining, confidence, entropy }` |

### Data

| Function | Description |
|----------|-------------|
| `loadPrograms()` | All 30,809 SNIES programs (17,230 active) |
| `loadItems(language)` | 48 IPIP items in `"es"` or `"en"` |
| `loadMapping()` | RIASEC → CINE field weights |
| `getCINEFields(programs)` | Unique CINE broad fields |
| `getDepartments(programs)` | Unique departments |

### Recommendations

| Function | Description |
|----------|-------------|
| `recommend(config)` | Rank programs by profile fit, with enrollment priors and regional boosts |

### Scoring Internals

| Function | Description |
|----------|-------------|
| `uniformPrior()` | Dirichlet α = (1,1,1,1,1,1) |
| `updateAlpha(alpha, type, response, keyed)` | Bayesian update after one answer |
| `posteriorMean(alpha)` | E[θ_k] = α_k / Σα |
| `entropy(alpha)` | Shannon entropy in bits |
| `confidence(alpha)` | 1 − (entropy / max_entropy) |
| `cosineSimilarity(a, b)` | Vector similarity [0, 1] |
| `expectedInfoGain(alpha, type)` | Information gain for adaptive item selection |

## How It Works

1. **Dirichlet prior** — starts with uniform belief over 6 RIASEC types
2. **Adaptive selection** — picks the question that maximizes expected information gain
3. **Bayesian update** — each Likert response updates the posterior
4. **Entropy stopping** — stops when Shannon entropy < 1.5 bits (~12 questions)
5. **Program matching** — cosine similarity between profile and CINE field vectors
6. **Enrollment priors** — downweights oversaturated fields, boosts underserved ones

## Data

Bundled in the package (no network requests):

- **30,809 programs** from Colombia's SNIES/HECAA catalog (24 columns each)
- **48 IPIP items** in English and Spanish (8 per RIASEC type)
- **RIASEC → CINE mapping** with weighted associations

## Also Available

- **Python**: `pip install riasec-co` — [PyPI](https://pypi.org/project/riasec-co/)
- **R**: `remotes::install_github("afromero/riasec-co", subdir = "r")`
- **React components**: [`riasec-co-react`](https://www.npmjs.com/package/riasec-co-react)

## License

MIT
