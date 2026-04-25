# Metodología

Metodología científica del motor de orientación vocacional `riasec-co`.

> Disponible en inglés: [METHODOLOGY.en.md](./METHODOLOGY.en.md).

## 1. Fundamento teórico

### Teoría RIASEC de Holland

La teoría de Holland (1997) sobre personalidades vocacionales propone que las personas y los entornos laborales pueden clasificarse en seis tipos:

| Tipo | Descripción | Ocupaciones de ejemplo |
|------|-------------|------------------------|
| **R** Realista | Práctico, manual, mecánico | Ingenieros, agricultores, mecánicos |
| **I** Investigador | Analítico, intelectual, científico | Científicos, investigadores, médicos |
| **A** Artístico | Creativo, original, expresivo | Artistas, escritores, diseñadores |
| **S** Social | Ayudar, enseñar, orientar | Docentes, orientadores, enfermería |
| **E** Emprendedor | Liderar, persuadir, gestionar | Gerentes, vendedores, abogados |
| **C** Convencional | Organizar, atención al detalle | Contadores, administradores, TI |

La satisfacción laboral se maximiza cuando el tipo de la persona coincide con su entorno de trabajo (congruencia persona-entorno). Los metaanálisis confirman esta relación: Nye et al. (2012) encontraron que los intereses vocacionales predicen el desempeño (rho = .14-.28), y Hoff et al. (2020) encontraron que la coincidencia de intereses predice la satisfacción laboral (rho = .19, IC 95% [.16, .21], k = 105 estudios, N = 39.602).

### Marcadores RIASEC IPIP

Usamos los 48 ítems de IPIP Basic Interest Markers desarrollados por Liao, Armstrong y Rounds (2008). Son ítems de dominio público validados contra el Self-Directed Search (SDS) de Holland. Cada ítem carga principalmente sobre un tipo RIASEC y se responde en escala Likert de 1 a 5.

La adaptación al español sigue a Cupani, Moran, Azpilicueta y Piccolo (2019), quienes desarrollaron y validaron una versión rioplatense en muestras universitarias argentinas.

**Propiedades de los ítems:**
- 8 ítems por tipo RIASEC (48 en total)
- Todos formulados en positivo
- Escala de respuesta Likert de 1 a 5
- Dominio público (sin restricciones de licencia)

## 2. Test adaptativo bayesiano

### Modelo Dirichlet-categórico

Modelamos el perfil RIASEC del estudiante como una distribución categórica sobre 6 tipos, con un prior conjugado Dirichlet:

```
θ ~ Dirichlet(α₁, α₂, ..., α₆)
```

**Prior:** α = (1, 1, 1, 1, 1, 1) — uniforme (sin preferencia previa).

**Actualización posterior:** después de observar una respuesta r (1-5) en un ítem del tipo k con codificación positiva:

```
α_k ← α_k + (r - 1) / 4
```

Esto normaliza la respuesta al intervalo [0, 1] y acumula evidencia para el tipo k. Una respuesta de 1 ("muy impreciso") aporta 0 evidencia; una respuesta de 5 ("muy preciso") aporta 1 unidad.

**Media posterior (perfil esperado):**

```
E[θ_k] = α_k / Σ α_j
```

### Selección adaptativa de ítems

En cada paso, seleccionamos el ítem que maximiza la ganancia de información esperada, medida como la divergencia KL esperada entre la posterior antes y después de responder:

```
item* = argmax_i E_r[ D_KL( p(θ | data, r_i) || p(θ | data) ) ]
```

Aproximamos esto simulando tres valores de respuesta (1, 3, 5) con peso igual y promediando la divergencia KL.

### Regla de detención

El test termina cuando se cumple una de estas condiciones:

1. **Umbral de entropía:** la entropía de Shannon de la media posterior cae por debajo de un umbral configurable (por defecto: 1.5 bits). La entropía máxima para 6 categorías es log₂(6) ≈ 2.585 bits.
2. **Máximo de preguntas:** un límite duro (por defecto: 24) evita tests excesivamente largos.
3. **Mínimo de preguntas:** se hacen siempre al menos 12 para garantizar cobertura suficiente.

En modo "completo", se administran los 48 ítems independientemente de la entropía.

### Métrica de confianza

Definimos la confianza como:

```
confianza = 1 - H(θ) / H_max
```

Donde H(θ) es la entropía de Shannon de la media posterior y H_max = log₂(6). La confianza va de 0 (uniforme, sin información) a 1 (toda la masa de probabilidad sobre un tipo).

## 3. Datos de programas SNIES

### Fuente

El catálogo completo de programas de educación superior colombianos proviene del SNIES (Sistema Nacional de Información de la Educación Superior), administrado por el Ministerio de Educación Nacional de Colombia. Los datos se acceden a través del portal HECAA en hecaa.mineducacion.gov.co.

### Cobertura

- **30.809 programas en total** (17.230 activos, 13.579 inactivos)
- **33 departamentos** (todos los departamentos colombianos + Bogotá D.C.)
- **10 campos amplios CINE F 2013 AC** (+ 1 categoría genérica)
- **33 campos específicos**, **80+ campos detallados**
- **Metadatos del programa:** institución, modalidad (presencial/virtual/distancia), nivel educativo, créditos, costo de matrícula, clasificación CINE

### Clasificación CINE

Los programas se clasifican usando CINE F 2013 AC (Clasificación Internacional Normalizada de la Educación: Campos de educación y capacitación), la adaptación colombiana del ISCED-F 2013 de la UNESCO.

## 4. Mapeo RIASEC → CINE

Mapeamos los tipos RIASEC de Holland a los campos amplios CINE F 2013 AC con base en el contenido ocupacional de cada campo. El mapeo usa pesos en [0, 1] para representar la fuerza de la asociación:

| Tipo RIASEC | Campos CINE primarios (peso 1.0) | Campos secundarios (peso 0.5-0.7) |
|-------------|-----------------------------------|-----------------------------------|
| R (Realista) | Agropecuario; Ingeniería | Servicios |
| I (Investigador) | Ciencias Naturales; Salud | TIC; Ingeniería |
| A (Artístico) | Arte y Humanidades | Ciencias Sociales |
| S (Social) | Educación; Salud | Ciencias Sociales |
| E (Emprendedor) | Administración y Derecho | Servicios |
| C (Convencional) | TIC | Administración |

Este mapeo está almacenado en `data/canonical/mapping.json` y los consumidores pueden sobrescribirlo.

## 5. Motor de recomendaciones

### Modelo de puntaje

Para cada programa calculamos:

```
puntaje(programa) = similitud(perfil_estudiante, perfil_campo)
                  × prior(programa)
```

**Similitud:** similitud coseno entre el vector de perfil RIASEC del estudiante y el vector del campo CINE del programa (derivado del mapeo).

**Prior:** ajustes multiplicativos configurables:

```
prior = base
      × (1 + pesoMatricula × log(N_total / N_campo))
      × (1 + impulsoRegional × estaEnRegion)
      × (1 + impulsoVirtual × esVirtual)
```

### Priors ponderados por matrícula

La innovación clave es el prior ponderado por matrícula. Con un `pesoMatricula` negativo (por defecto: -0.3), los campos con alta matrícula (por ejemplo, Administración de Empresas y Derecho con 10.686 programas) reciben menor peso relativo a campos con baja matrícula (por ejemplo, Agropecuario con 1.150 programas).

La escala logarítmica garantiza que el efecto sea proporcional: un campo con 10 veces menos programas se impulsa en aproximadamente 0.7 unidades. Esto naturalmente sube programas en campos menos saturados como Acuicultura o Ciencia Ambiental sobre los omnipresentes programas de Administración de Empresas, cuando la coincidencia RIASEC es igual.

### Impulsos regional y virtual

- **Impulso regional:** los programas en los departamentos especificados por el estudiante reciben un impulso multiplicativo. Para estudiantes en regiones rurales como San Jorge y La Mojana (Sucre/Córdoba/Bolívar), esto saca a la luz opciones locales accesibles sin tener que reubicarse.
- **Impulso virtual:** los programas virtuales y a distancia reciben un impulso, reconociendo que el acceso geográfico es una barrera primaria para estudiantes rurales.

## 6. Limitaciones y trabajo futuro

1. **Banco de ítems:** los 48 ítems IPIP son un instrumento de tamizaje, no diagnóstico. Para orientación vocacional clínica debe usarse el SDS completo o un instrumento colombiano validado.
2. **Mapeo RIASEC → CINE:** el mapeo actual es curado por el autor con base en la tipología clásica de Holland, no validado psicométricamente de forma independiente contra criterios externos como los perfiles RIASEC del sistema O*NET. Trabajos futuros deberían validarlo contra resultados de empleo colombianos. Pull requests con pesos derivados empíricamente son bienvenidos.
3. **Datos de matrícula:** la versión actual usa el conteo de programas como aproximación a la matrícula. Versiones futuras incorporarán estadísticas reales de matrícula desde la API REST de HECAA.
4. **Modelo IRT:** el modelo actual usa una actualización Dirichlet simplificada. Un modelo de teoría de respuesta al ítem (IRT) completo (por ejemplo, Graded Response Model) con parámetros de ítem calibrados mejoraría la precisión de la medición.
5. **Adaptación cultural:** aunque los ítems en español están adaptados de Cupani et al. (2019) — versión rioplatense validada en muestras universitarias argentinas — no han sido específicamente validados en el contexto colombiano con poblaciones estudiantiles rurales.

## Referencias

- Cupani, M., Moran, V. E., Azpilicueta, A. E., y Piccolo, N. V. (2019). Alternate Forms Public Domain RIASEC Markers for Interests and Self-Efficacy: Spanish version. *Electronic Journal of Research in Educational Psychology*, 17(2), 359-382. [DOI: 10.25115/ejrep.v17i48.2136](https://ojs.ual.es/ojs/index.php/EJREP/article/view/2136)
- Holland, J. L. (1997). *Making vocational choices: A theory of vocational personalities and work environments* (3ra ed.). Psychological Assessment Resources. [archive.org](https://archive.org/details/makingvocational0000holl)
- Liao, H.-Y., Armstrong, P. I., y Rounds, J. (2008). Development and initial validation of public domain Basic Interest Markers. *Journal of Vocational Behavior*, 73(1), 159-183. [DOI: 10.1016/j.jvb.2007.12.002](https://doi.org/10.1016/j.jvb.2007.12.002)
- Nye, C. D., Su, R., Rounds, J., y Drasgow, F. (2012). Vocational interests and performance: A quantitative summary of over 60 years of research. *Perspectives on Psychological Science*, 7(4), 384-403. [PubMed: 26168474](https://pubmed.ncbi.nlm.nih.gov/26168474/)
- Nye, C. D., Prasad, J., Bradburn, J., y Elizondo, F. (2018). Improving the operationalization of interest congruence using polynomial regression. *Journal of Vocational Behavior*, 104, 154-169. [DOI: 10.1016/j.jvb.2017.10.012](https://doi.org/10.1016/j.jvb.2017.10.012)
- Hoff, K. A., Song, Q. C., Wee, C. J. M., Phan, W. M. J., y Rounds, J. (2020). Interest fit and job satisfaction: A systematic review and meta-analysis. *Journal of Vocational Behavior*, 123, 103503. [DOI: 10.1016/j.jvb.2020.103503](https://doi.org/10.1016/j.jvb.2020.103503)
- Nye, C. D., Prasad, J., y Rounds, J. (2021). The effects of vocational interests on motivation, satisfaction, and academic performance: Test of a mediated model. *Journal of Vocational Behavior*, 127, 103583. [Elsevier](https://linkinghub.elsevier.com/retrieve/pii/S0001879121000555)
- van der Linden, W. J., y Hambleton, R. K. (Eds.). (2018). *Handbook of Item Response Theory*. CRC Press.
- SNIES, Ministerio de Educación Nacional de Colombia. [Buscador público de programas](https://hecaa.mineducacion.gov.co/consultaspublicas/programas)
- International Personality Item Pool. [ipip.ori.org](https://ipip.ori.org/)
