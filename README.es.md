# riasec-co

Motor bayesiano adaptativo de orientacion vocacional RIASEC para Colombia.

Combina un cuestionario de 48 items del [IPIP](https://ipip.ori.org/) con el catalogo completo del [SNIES](https://hecaa.mineducacion.gov.co/consultaspublicas/programas) (17.230 programas activos). Priors ponderados por matricula visibilizan programas poco conocidos por encima de campos sobresaturados. Disponible como paquetes para **TypeScript/JavaScript**, **Python** y **R**.

## Instalar

### TypeScript / JavaScript

```bash
npm install @riasec-co/core
# Componentes React (opcional):
npm install @riasec-co/react
```

### Python

```bash
pip install riasec-co
```

### R

```r
# install.packages("riasecco")  # CRAN (proximamente)
# O desde GitHub:
# remotes::install_github("afromero/riasec-co", subdir = "r")
```

## Inicio Rapido

### TypeScript

```typescript
import { createQuiz, loadPrograms, recommend } from '@riasec-co/core'

const quiz = createQuiz({ language: 'es', mode: 'adaptive' })

let q = quiz.nextQuestion()
quiz.answer(q.id, 4) // Escala Likert 1-5

// Despues de completar el cuestionario:
const programs = loadPrograms()
const results = recommend({
  profile: quiz.profile(),
  programs,
  filters: { departments: ['Sucre', 'Cordoba'], active: true },
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
    departments=["Sucre", "Cordoba"],
    limit=20,
)
# Retorna un DataFrame de Polars
```

### R

```r
library(riasecco)

data(programs)  # 30.809 programas como data.frame
data(items_es)  # 48 items IPIP en espanol

quiz <- create_quiz(language = "es")
q <- next_question(quiz)
answer(quiz, q$id, 4L)

results <- recommend(profile(quiz), departments = "Sucre")
```

## Como Funciona

1. **Prior Dirichlet**: Comienza con creencia uniforme sobre 6 tipos RIASEC
2. **Seleccion adaptativa**: Elige la pregunta que maximiza la ganancia de informacion esperada (divergencia KL)
3. **Actualizacion bayesiana**: Cada respuesta actualiza el posterior Dirichlet
4. **Parada por entropia**: Se detiene cuando el perfil tiene suficiente confianza (~12 preguntas en modo adaptativo)
5. **Emparejamiento de programas**: Similitud coseno entre el perfil del estudiante y los vectores de campo CINE
6. **Priors por matricula**: Penaliza campos sobresaturados, impulsa programas regionales y virtuales

## Fuentes de Datos

| Fuente | Descripcion | Acceso |
|--------|-------------|--------|
| [SNIES/HECAA](https://hecaa.mineducacion.gov.co/consultaspublicas/programas) | 30.809 programas de educacion superior (17.230 activos) | Publico, descargado del portal HECAA |
| [IPIP](https://ipip.ori.org/) | 48 marcadores de intereses RIASEC de dominio publico | Dominio publico |
| Mapeo RIASEC→CINE | Mapeo experto de tipos Holland a campos CINE F 2013 AC | Original, incluido en el paquete |

## Estructura del Repositorio

```
riasec-co/
├── data/canonical/        # Datos canonicos (CSV + JSON)
├── packages/core/         # Motor TypeScript (sin dependencias)
├── packages/react/        # Componentes React
├── python/                # Paquete Python (Polars)
├── r/                     # Paquete R (listo para CRAN)
├── scripts/               # Pipeline de datos
└── .github/workflows/     # CI/CD
```

## Desarrollo

```bash
# Pipeline de datos
npm install
npm run update-snies    # Parsear Excel SNIES → CSV
npm run validate        # Validar todos los archivos de datos

# TypeScript
cd packages/core && npm install && npm run ci

# Python
cd python && uv venv && source .venv/bin/activate
uv pip install -e ".[dev]" && pytest

# R
Rscript r/data-raw/generate.R
R CMD check r/
```

## Contexto

Los estudiantes rurales colombianos en regiones como San Jorge y La Mojana carecen de acceso a orientacion vocacional. Las herramientas existentes son centradas en EE.UU. (O*NET), encerradas detras de formularios web gubernamentales (SNIES/HECAA), o inexistentes como paquetes de codigo abierto. Ningun paquete en npm, PyPI o CRAN combina evaluacion vocacional con datos nacionales de educacion superior — en ningun pais.

`riasec-co` llena este vacio: un motor de cuestionario RIASEC bayesiano adaptativo emparejado con la base de datos completa de programas SNIES de Colombia (17.230 programas activos), publicado como paquetes para JS/TS, Python y R.

## Referencias

- Holland, J. L. (1997). *Making vocational choices*. Psychological Assessment Resources.
- Liao, H.-Y., Armstrong, P. I., & Rounds, J. (2008). Development and initial validation of public domain Basic Interest Markers. *Journal of Vocational Behavior*, 73(1), 159-183.
- Armstrong, P. I., Allison, W., & Rounds, J. (2020). Alternate Forms Public Domain RIASEC Markers. *Electronic Journal of Research in Educational Psychology*.
- SNIES, Ministerio de Educacion Nacional de Colombia. https://hecaa.mineducacion.gov.co/consultaspublicas/programas
- IPIP: International Personality Item Pool. https://ipip.ori.org/

## Licencia

MIT
