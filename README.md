<div align="center">

# riasec-co

**El primer paquete de código abierto que combina evaluación vocacional con datos nacionales de educación superior.**

Motor bayesiano adaptativo RIASEC con el catálogo completo SNIES de Colombia — 17.230 programas activos en 33 departamentos. Disponible para TypeScript, Python y R.

[![CI](https://github.com/affromero/riasec-co/actions/workflows/ci.yml/badge.svg)](https://github.com/affromero/riasec-co/actions/workflows/ci.yml)
[![npm](https://img.shields.io/npm/v/riasec-co)](https://www.npmjs.com/package/riasec-co)
[![PyPI](https://img.shields.io/pypi/v/riasec-co)](https://pypi.org/project/riasec-co/)
[![TypeScript](https://img.shields.io/badge/TypeScript-strict-blue)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776ab)](https://www.python.org/)
[![R](https://img.shields.io/badge/R-4.1+-276dc3)](https://www.r-project.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

[Read in English](README.en.md)

</div>

> **30.809** programas | **17.230** activos | **297** instituciones | **33** departamentos | **11** campos CINE

## ¿Por Qué Existe Esto?

En Colombia, **decidir qué estudiar** es una decisión que la mayoría de los estudiantes toman casi sin orientación. Los estudiantes rurales en regiones como San Jorge y La Mojana no tienen acceso a un orientador vocacional, no existen herramientas de evaluación en español, y no hay forma de descubrir programas más allá de las pocas universidades que conocen. La herramienta oficial (SNIES) es un buscador de datos crudos — te dice *qué* existe, pero no *qué te conviene*.

Mientras tanto, el marco vocacional estándar a nivel mundial (la teoría RIASEC de Holland) tiene **cero implementaciones de código abierto** como paquetes instalables en npm, PyPI o CRAN. Cada aplicación RIASEC en internet es un formulario cerrado que te da un código de letras y nada más.

`riasec-co` resuelve ambos problemas:

- **Un motor psicométrico real** — no un quiz de juguete. Testing adaptativo bayesiano con posteriores Dirichlet, parada basada en entropía, y selección de ítems por teoría de la información. Menos preguntas, perfiles más precisos.
- **Emparejado con programas reales** — cada recomendación se mapea a un programa real del catálogo SNIES de Colombia, con institución, departamento, modalidad y costo de matrícula.
- **Priors ponderados por matrícula** — el algoritmo contrarresta activamente la sobresaturación. En vez de recomendar otra carrera de Administración de Empresas (5.887 en el sistema), visibiliza Acuicultura, Ciencias Ambientales, y otros campos donde la demanda supera la oferta.
- **Tres lenguajes, un motor** — paquetes para TypeScript, Python y R que comparten los mismos datos y producen los mismos resultados. Investigadores pueden usar los datos en pandas/polars/tidyverse. Desarrolladores pueden integrar el quiz en cualquier app.
- **Completamente abierto** — ítems de dominio público (IPIP), datos públicos (SNIES), licencia MIT. Sin vendor lock-in, sin API keys, sin paywalls.

Este es el **primer paquete que combina evaluación vocacional con datos nacionales de educación superior**, en cualquier país.

---

## De un Vistazo

### Perfil RIASEC adaptativo

El motor bayesiano converge en el perfil del estudiante en ~12 preguntas. Arriba, el perfil resultante. Abajo, cómo las probabilidades se estabilizan y la entropía cae con cada respuesta.

<p align="center">
  <img src="docs/assets/profile-radar.png" alt="Gráfico radar RIASEC" width="520"><br>
  <img src="docs/assets/adaptive-convergence.png" alt="Convergencia adaptativa" width="720">
</p>

### 17.230 programas activos por campo CINE

![Distribución por campo CINE](docs/assets/cine-distribution.png)

### Brecha regional: Sucre + Córdoba + Bolívar vs. nacional

Solo **1.091 programas** atienden a 3 departamentos con más de 3.5M de habitantes. La región tiene menos posgrados y más programas técnicos que el promedio nacional.

![Comparación regional](docs/assets/regional-comparison.png)

### Top 10 recomendaciones para un estudiante Investigador

Los priors por matrícula penalizan campos sobresaturados (Administración y Derecho: 5.887 programas) e impulsan campos más pequeños. Programas virtuales reciben un boost de 1.5x.

![Recomendaciones de programas](docs/assets/recommendations.png)

---

## Instalar

```bash
# TypeScript / JavaScript — desde GitHub
npm install github:afromero/riasec-co#main --workspace=packages/core

# Python — desde GitHub
pip install "riasec-co @ git+https://github.com/afromero/riasec-co.git#subdirectory=python"
```

```r
# R — desde GitHub
remotes::install_github("afromero/riasec-co", subdir = "r")
```

## Uso: Tres Lenguajes, Un Motor

Los tres paquetes comparten los mismos datos y producen los mismos resultados.

### TypeScript

```typescript
import { createQuiz, loadPrograms, recommend } from 'riasec-co'

// 1. Ejecutar cuestionario adaptativo
const quiz = createQuiz({ language: 'es', mode: 'adaptive' })
while (!quiz.isComplete()) {
  const q = quiz.nextQuestion()!
  const response = await askUser(q.text) // tu interfaz
  quiz.answer(q.id, response)
}

console.log(quiz.profile())
// { R: 0.19, I: 0.27, A: 0.10, S: 0.16, E: 0.10, C: 0.18 }
console.log(quiz.topTypes(2)) // ['I', 'R']

// 2. Obtener recomendaciones
const results = recommend({
  profile: quiz.profile(),
  programs: loadPrograms(),
  filters: { departments: ['Sucre', 'Córdoba', 'Bolívar'], active: true },
  priors: { enrollmentWeight: -0.3, virtualBoost: 1.5 },
  limit: 10,
})

results.forEach((r, i) =>
  console.log(`${i + 1}. ${r.program.nombre_programa} (${r.score.toFixed(2)})`)
)
```

### Python

```python
from riasec_co import Quiz, Programs, recommend

# 1. Ejecutar cuestionario adaptativo
quiz = Quiz(language="es", mode="adaptive")
while not quiz.is_complete:
    q = quiz.next_question()
    response = ask_user(q.text)  # tu interfaz
    quiz.answer(q.id, response)

print(quiz.profile)
# {'R': 0.19, 'I': 0.27, 'A': 0.10, 'S': 0.16, 'E': 0.10, 'C': 0.18}
print(quiz.top_types(2))  # ['I', 'R']

# 2. Obtener recomendaciones (retorna DataFrame de Polars)
results = recommend(
    quiz.profile,
    departments=["Sucre", "Córdoba", "Bolívar"],
    enrollment_weight=-0.3,
    virtual_boost=1.5,
    limit=10,
)
print(results.select("nombre_programa", "nombre_institucion", "score"))

# 3. Investigadores: solo usen los datos
df = Programs.load()  # DataFrame de Polars, 30.809 filas
df.filter(pl.col("departamento") == "Sucre").group_by("cine_amplio").len()
```

### R

```r
library(riasecco)

# 1. Acceder a los datos directamente
data(programs)   # 30.809 programas
data(items_es)   # 48 ítems IPIP (español)

programs |>
  subset(departamento == "Sucre" & estado == "Activo") |>
  with(table(cine_amplio))

# 2. Ejecutar cuestionario adaptativo
quiz <- create_quiz(language = "es")
while (!is_complete(quiz)) {
  q <- next_question(quiz)
  response <- ask_user(q$text)  # tu interfaz
  answer(quiz, q$id, response)
}

profile(quiz)
# R: 0.19, I: 0.27, A: 0.10, S: 0.16, E: 0.10, C: 0.18

# 3. Obtener recomendaciones
results <- recommend(profile(quiz), departments = c("Sucre", "Córdoba"))
head(results[, c("nombre_programa", "nombre_institucion", "score")])
```

## ¿Por Qué Bayes?

### La versión simple

Imagina que estás adivinando el sabor favorito de helado de alguien, pero solo puedes hacerle preguntas de sí o no. Un test normal le preguntaría las 20 preguntas sin importar qué — incluso si después de 5 preguntas ya es obvio que le encanta el chocolate.

Nuestro motor es más inteligente: **empieza sin saber nada**, y con cada respuesta actualiza lo que cree saber. Si después de unas pocas preguntas ya está bastante seguro de tu perfil, **se detiene**. Si todavía hay duda entre dos tipos, pregunta específicamente sobre esos. Esto se llama *inferencia bayesiana* — aprender de la evidencia de forma óptima.

El resultado: en vez de 48 preguntas, típicamente bastan **~12** para obtener un perfil confiable. Para un estudiante respondiendo en el celular con datos limitados, eso es la diferencia entre terminar el test o abandonarlo.

### El problema del bibliotecario

Hay un ejemplo famoso en probabilidad (Kahneman & Tversky): *"Steve es tímido, ordenado, meticuloso y le apasiona el detalle. ¿Es más probable que sea bibliotecario o agricultor?"*

La mayoría dice bibliotecario — la descripción encaja perfecto. Pero hay **20 veces más agricultores que bibliotecarios**. Cuando consideras esa tasa base, Steve probablemente es agricultor con gustos de bibliotecario.

Esto es exactamente lo que hacen nuestros **priors por matrícula**. Sin ellos, un estudiante Emprendedor siempre recibiría Administración de Empresas — porque el perfil encaja y hay 5.887 programas. Pero igual que con Steve, el hecho de que hay tantos programas es justamente la razón para buscar alternativas. Con el prior bayesiano, el motor ajusta: "sí, Administración encaja, pero también encajan Logística, Comercio Internacional y Negocios Digitales — y esos campos tienen mucha menos competencia."

El pensamiento bayesiano dice: no solo mires qué tan bien encaja la evidencia — mira también qué tan común es cada opción. Eso transforma una recomendación genérica en una recomendación útil.

### La versión técnica

La mayoría de tests vocacionales en línea usan **puntuación simple**: suman tus respuestas por tipo y te dan el más alto. Esto tiene tres problemas fundamentales:

1. **Necesitas responder todas las preguntas** — no hay forma de parar temprano porque no sabes cuánta información ya tienes.
2. **Todas las preguntas pesan igual** — la pregunta 47 aporta lo mismo que la pregunta 1, aunque tu perfil ya esté claro.
3. **No hay medida de certeza** — te dice "eres Investigador" pero no si es con 95% o 51% de confianza.

La inferencia bayesiana resuelve los tres problemas:

### Cómo funciona, paso a paso

**Antes de empezar**, el motor no sabe nada sobre ti. Representa esa ignorancia como una distribución uniforme sobre los 6 tipos RIASEC — cada uno tiene la misma probabilidad (16.7%). Matemáticamente esto es un **prior Dirichlet** con α = (1, 1, 1, 1, 1, 1).

**Con cada respuesta**, el motor actualiza sus creencias. Si respondes "5 — Muy preciso" a "Me gusta resolver problemas complejos" (un ítem Investigador), el parámetro α_I sube. Después de varias respuestas, la distribución se concentra en los tipos que realmente te describen.

**La selección adaptativa** elige la siguiente pregunta basándose en cuál reduciría más la incertidumbre. Si ya está claro que no eres Artístico pero aún no distingue entre Investigador y Convencional, preguntará sobre esos dos — no perderá tiempo en preguntas cuya respuesta ya puede predecir.

**La parada automática** mide la entropía de Shannon (incertidumbre) del perfil. Cuando cae por debajo de 1.5 bits (de un máximo de 2.585), el cuestionario se detiene. Esto típicamente ocurre en **~12 preguntas** en vez de las 48 del test completo.

### ¿Por qué importa aquí?

Para un estudiante rural en Sucre respondiendo en el celular de un familiar, la diferencia entre 48 preguntas y 12 es la diferencia entre completar el test o abandonarlo. El enfoque bayesiano hace que cada pregunta cuente — y le da al estudiante (y al orientador) una medida cuantitativa de qué tan seguro es el resultado.

### El motor en un diagrama

```
      Prior Dirichlet           Selección Adaptativa de Ítems      Parada por Entropía
   α = (1,1,1,1,1,1)     -->  argmax E[KL(post || prior)]   -->  H(θ) < 1.5 bits?
            |                            |                                |
   Actualización Bayesiana      Siguiente Pregunta              Perfil RIASEC
   α_k += (r-1)/4               Ítem más informativo            {R:.19 I:.27 A:.10 ...}
            |                            |                                |
            '------------ ciclo ---------'                       Emparejamiento
                                                                  coseno(perfil, CINE)
                                                                  × prior matrícula
                                                                  × boost regional
                                                                  × boost virtual
```

1. **Prior Dirichlet** — Creencia uniforme sobre 6 tipos RIASEC
2. **Selección adaptativa** — Elige la pregunta que maximiza la divergencia KL esperada
3. **Actualización bayesiana** — Cada respuesta Likert (1-5) actualiza el posterior Dirichlet
4. **Parada por entropía** — Se detiene cuando la entropía de Shannon cae bajo el umbral (~12 preguntas)
5. **Emparejamiento de programas** — Similitud coseno entre perfil y vectores de campo CINE
6. **Priors por matrícula** — `log(N_total / N_campo)` penaliza campos sobresaturados

## Estadísticas Clave

| Métrica | Valor |
|---------|-------|
| Total programas en SNIES | 30.809 |
| Programas activos | 17.230 |
| Instituciones | 297 |
| Departamentos | 33 (32 + Bogotá D.C.) |
| Campos amplios CINE | 11 |
| Programas virtuales/distancia | 2.736 (15,9%) |
| Sector público | 6.446 (37,4%) |
| Sector privado | 10.784 (62,6%) |
| Ítems IPIP por idioma | 48 (8 por tipo RIASEC) |
| Preguntas del cuestionario adaptativo | ~12 (mín 12, máx 24) |

## Fuentes de Datos

| Fuente | Qué | Tamaño |
|--------|-----|--------|
| [SNIES/HECAA](https://hecaa.mineducacion.gov.co/consultaspublicas/programas) | Catálogo completo de educación superior colombiana | 30.809 programas, 39 campos |
| [IPIP](https://ipip.ori.org/) | Marcadores de intereses RIASEC de dominio público | 48 ítems (en + es) |
| Mapeo RIASEC-CINE | Tipos Holland a campos CINE F 2013 AC | 16 asociaciones ponderadas |

## Desarrollo

```bash
# Pipeline de datos
npm install
npm run update-snies          # Parsear Excel SNIES → programs.csv
npm run validate              # Validar todos los archivos

# TypeScript
cd packages/core
npm install && npm run ci     # type-check + 41 tests

# Python
cd python
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
pytest                        # 35 tests

# R
Rscript r/data-raw/generate.R
R CMD check r/
```

## Referencias

- Holland, J. L. (1997). *Making vocational choices*. Psychological Assessment Resources.
- Liao, H.-Y., Armstrong, P. I., & Rounds, J. (2008). Development and initial validation of public domain Basic Interest Markers. *Journal of Vocational Behavior*, 73(1), 159-183.
- Armstrong, P. I., Allison, W., & Rounds, J. (2020). Alternate Forms Public Domain RIASEC Markers. *Electronic Journal of Research in Educational Psychology*.
- Nye, C. D., Su, R., Rounds, J., & Drasgow, F. (2012). Vocational interests and performance. *Perspectives on Psychological Science*, 7(4), 384-403.
- SNIES, Ministerio de Educación Nacional de Colombia.
- IPIP: International Personality Item Pool.

Ver [METHODOLOGY.md](METHODOLOGY.md) para la metodología científica completa.

## Licencia

MIT
