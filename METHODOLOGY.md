# Methodology

Scientific methodology for the `riasec-co` vocational guidance engine.

## 1. Theoretical Foundation

### Holland's RIASEC Theory

Holland's (1997) theory of vocational personalities posits that people and work environments can be classified into six types:

| Type | Description | Example Occupations |
|------|-------------|-------------------|
| **R** Realistic | Hands-on, practical, mechanical | Engineers, farmers, mechanics |
| **I** Investigative | Analytical, intellectual, scientific | Scientists, researchers, doctors |
| **A** Artistic | Creative, original, expressive | Artists, writers, designers |
| **S** Social | Helping, teaching, counseling | Teachers, counselors, nurses |
| **E** Enterprising | Leading, persuading, managing | Managers, salespeople, lawyers |
| **C** Conventional | Organizing, detail-oriented | Accountants, administrators, IT |

Career satisfaction is maximized when a person's type matches their work environment (person-environment congruence). Meta-analyses confirm this relationship: Nye et al. (2012) found vocational interests predict performance (rho = .14-.28), and Nye et al. (2020) found interest congruence predicts job satisfaction (rho = .17-.36).

### IPIP RIASEC Markers

We use the 48-item IPIP Basic Interest Markers developed by Liao, Armstrong & Rounds (2008). These are public-domain items validated against Holland's Self-Directed Search (SDS). Each item loads primarily on one RIASEC type and is rated on a 1-5 Likert scale.

The Spanish adaptation follows Armstrong, Allison & Rounds (2020), who validated alternate forms of the IPIP RIASEC markers across languages.

**Item properties:**
- 8 items per RIASEC type (48 total)
- All positively keyed
- 1-5 Likert response scale
- Public domain (no licensing restrictions)

## 2. Bayesian Adaptive Testing

### Dirichlet-Categorical Model

We model the student's RIASEC profile as a categorical distribution over 6 types, with a Dirichlet conjugate prior:

```
θ ~ Dirichlet(α₁, α₂, ..., α₆)
```

**Prior:** α = (1, 1, 1, 1, 1, 1) — uniform (no prior preference)

**Posterior update:** After observing a response r (1-5) on an item of type k with positive keying:

```
α_k ← α_k + (r - 1) / 4
```

This normalizes the response to [0, 1] and accumulates evidence for type k. A response of 1 ("very inaccurate") adds 0 evidence; a response of 5 ("very accurate") adds 1 unit.

**Posterior mean (expected profile):**

```
E[θ_k] = α_k / Σ α_j
```

### Adaptive Item Selection

At each step, we select the item that maximizes expected information gain, measured as the expected KL divergence between the posterior before and after answering:

```
item* = argmax_i E_r[ D_KL( p(θ | data, r_i) || p(θ | data) ) ]
```

We approximate this by simulating three response values (1, 3, 5) with equal weight and computing the average KL divergence.

### Stopping Rule

The quiz stops when one of these conditions is met:

1. **Entropy threshold:** Shannon entropy of the posterior mean drops below a configurable threshold (default: 1.5 bits). Maximum entropy for 6 categories is log₂(6) ≈ 2.585 bits.
2. **Maximum questions:** A hard limit (default: 24) prevents excessively long quizzes.
3. **Minimum questions:** At least 12 questions are always asked to ensure sufficient coverage.

In "full" mode, all 48 items are administered regardless of entropy.

### Confidence Metric

We define confidence as:

```
confidence = 1 - H(θ) / H_max
```

Where H(θ) is the Shannon entropy of the posterior mean and H_max = log₂(6). Confidence ranges from 0 (uniform — no information) to 1 (all probability mass on one type).

## 3. SNIES Program Data

### Source

The complete catalog of Colombian higher education programs comes from the SNIES (Sistema Nacional de Informacion de la Educacion Superior), maintained by the Ministerio de Educacion Nacional de Colombia. The data is accessed through the HECAA portal at hecaa.mineducacion.gov.co.

### Coverage

- **30,809 total programs** (17,230 active, 13,579 inactive)
- **33 departments** (all Colombian departments + Bogota D.C.)
- **10 CINE F 2013 AC broad fields** (+ 1 generic category)
- **33 specific fields**, **80+ detailed fields**
- **Program metadata:** institution, modality (presencial/virtual/distancia), education level, credits, tuition cost, CINE classification

### CINE Classification

Programs are classified using the CINE F 2013 AC (Clasificacion Internacional Normalizada de la Educacion — Campos de educacion y capacitacion), the Colombian adaptation of UNESCO's ISCED-F 2013.

## 4. RIASEC → CINE Mapping

We map Holland's RIASEC types to CINE F 2013 AC broad fields based on the occupational content of each field. The mapping uses weights in [0, 1] to represent strength of association:

| RIASEC Type | Primary CINE Fields (weight 1.0) | Secondary Fields (weight 0.5-0.7) |
|-------------|----------------------------------|-----------------------------------|
| R (Realistic) | Agropecuario; Ingenieria | Servicios |
| I (Investigative) | Ciencias Naturales; Salud | TIC; Ingenieria |
| A (Artistic) | Arte y Humanidades | Ciencias Sociales |
| S (Social) | Educacion; Salud | Ciencias Sociales |
| E (Enterprising) | Administracion y Derecho | Servicios |
| C (Conventional) | TIC | Administracion |

This mapping is stored in `data/canonical/mapping.json` and is overridable by consumers.

## 5. Recommendation Engine

### Scoring Model

For each program, we compute:

```
score(program) = similarity(student_profile, field_profile)
              × prior(program)
```

**Similarity:** Cosine similarity between the student's RIASEC profile vector and the program's CINE field vector (derived from the mapping).

**Prior:** Configurable multiplicative adjustments:

```
prior = base
      × (1 + enrollmentWeight × log(N_total / N_field))
      × (1 + regionalBoost × isInRegion)
      × (1 + virtualBoost × isVirtual)
```

### Enrollment-Weighted Priors

The key innovation is the enrollment-weighted prior. With a negative `enrollmentWeight` (default: -0.3), fields with high enrollment (e.g., Administracion de Empresas y Derecho, with 10,686 programs) are downweighted relative to fields with low enrollment (e.g., Agropecuario with 1,150 programs).

The logarithmic scaling ensures the effect is proportional: a field with 10x fewer programs gets boosted by about 0.7 units. This naturally surfaces programs in less-saturated fields like Aquaculture or Environmental Science over ubiquitous Business Administration programs, when the RIASEC match is equal.

### Regional and Virtual Boosts

- **Regional boost:** Programs in the student's specified departments receive a multiplicative boost. For students in rural regions like San Jorge y La Mojana (Sucre/Cordoba/Bolivar), this surfaces local options they can access without relocating.
- **Virtual boost:** Virtual and distance programs receive a boost, recognizing that geographic access is a primary barrier for rural students.

## 6. Limitations and Future Work

1. **Item bank:** The 48-item IPIP markers are a screening instrument, not a diagnostic tool. For clinical vocational counseling, a full SDS or validated Colombian instrument should be used.
2. **RIASEC→CINE mapping:** The current mapping is expert-derived, not empirically validated against Colombian employment data. Future work should validate against employment outcomes.
3. **Enrollment data:** The current version uses program counts as a proxy for enrollment. Future versions will incorporate actual enrollment statistics from the HECAA REST API.
4. **IRT model:** The current model uses a simplified Dirichlet update. A full Item Response Theory model (e.g., Graded Response Model) with calibrated item parameters would improve measurement precision.
5. **Cultural adaptation:** While the Spanish items are adapted from Armstrong et al. (2020), they have not been specifically validated in the Colombian context with rural student populations.

## References

- Armstrong, P. I., Allison, W., & Rounds, J. (2020). Alternate Forms Public Domain RIASEC Markers. *Electronic Journal of Research in Educational Psychology*.
- Holland, J. L. (1997). *Making vocational choices: A theory of vocational personalities and work environments* (3rd ed.). Psychological Assessment Resources.
- Liao, H.-Y., Armstrong, P. I., & Rounds, J. (2008). Development and initial validation of public domain Basic Interest Markers. *Journal of Vocational Behavior*, 73(1), 159-183.
- Nye, C. D., Su, R., Rounds, J., & Drasgow, F. (2012). Vocational interests and performance: A quantitative summary of over 60 years of research. *Perspectives on Psychological Science*, 7(4), 384-403.
- Nye, C. D., Prasad, J., Bradburn, J., & Elizondo, F. (2020). Improving the operationalization of interest congruence using polynomial regression. *Journal of Vocational Behavior*, 118, 103370.
- van der Linden, W. J., & Hambleton, R. K. (Eds.). (2018). *Handbook of Item Response Theory*. CRC Press.
- SNIES, Ministerio de Educacion Nacional de Colombia. https://hecaa.mineducacion.gov.co/consultaspublicas/programas
- International Personality Item Pool. https://ipip.ori.org/
