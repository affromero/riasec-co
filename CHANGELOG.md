# Changelog

## [0.2.0] - 2026-04-25

### BREAKING

- `recommend()` now defaults to undergrad-entry programs only (Universitario, Tecnológico, Formación técnica profesional). The default audience is `"undergrad"` because most consumers of this package build vocational guidance for high-school graduates, and surfacing Doctorado / Maestría / Especialización suggestions to a 16-year-old is not meaningful guidance.
- Existing consumers who rely on getting all program levels back must now pass `filters: { audience: "all" }`. Existing consumers who pass an explicit `filters.nivel_formacion` array are unaffected — the explicit allowlist still overrides the audience default.

### Added

- `ProgramFilters.audience: "undergrad" | "all"` field. Default is `"undergrad"`. Explicit `nivel_formacion` array overrides this.
- `UNDERGRAD_LEVELS` exported constant for consumers that want to reuse the same level-filtering logic outside the recommender.
- 3 new tests in `__tests__/recommender.test.ts` covering the default filter, the `audience: "all"` opt-out, and the explicit-allowlist override.

## [0.1.3] - 2026-04-25

### Fixed

- **Spanish-version reference in `items_es.json` and all docs.** The previous citation ("Armstrong, Allison & Rounds, 2020. Alternate Forms Public Domain RIASEC Markers") was wrong on both authors and year. The actual paper that adapted the IPIP-BIM scale to Spanish (Río de la Plata variant) is Cupani, M., Moran, V. E., Azpilicueta, A. E., & Piccolo, N. V. (2019), *Electronic Journal of Research in Educational Psychology*, 17(2), 359-382 (DOI 10.25115/ejrep.v17i48.2136). Fixed in canonical data, R package extdata, METHODOLOGY (English + new Spanish), and both READMEs.
- **Inline citation in METHODOLOGY for the interest-fit/satisfaction meta-analysis.** Was attributed to "Nye et al. (2020)"; the correct meta-analysis with k=105 studies and N=39,602 is Hoff, K. A., Song, Q. C., Wee, C. J. M., Phan, W. M. J., & Rounds, J. (2020), JVB 123, 103503.
- **Year of the polynomial-regression citation.** Was listed as 2020; the paper (Nye, Prasad, Bradburn & Elizondo) was published online 2017, in print 2018, JVB 104, 154-169 (DOI 10.1016/j.jvb.2017.10.012).

### Added

- **Spanish translation of METHODOLOGY.md** as the default; English moved to METHODOLOGY.en.md (mirrors the README convention). Both READMEs cross-link.
- `reference_doi` and `reference_url` fields on `items_es.json` and `items_en.json` so consumers can verify the source citation without manual lookup. URLs verified by real-browser testing.
- `validation_status`, `contribution_invitation`, and `references` fields on `mapping.json`. The mapping is author-curated based on Holland (1997) and the SNIES CINE taxonomy; it has not been independently psychometrically validated against external criteria such as O*NET RIASEC interest profiles. Pull requests with empirically derived weights are welcome.
- All citation references in METHODOLOGY (both languages) and READMEs (both languages) now include direct, real-browser-verified DOI / publisher URLs.

### Changed

- `data/canonical/mapping.json`'s `source` description now reads "Author-curated weighted mapping..." (previously "Expert mapping...") for accuracy and transparency.
- METHODOLOGY's "Limitations" section now describes the RIASEC→CINE mapping consistently with the new mapping.json wording and explicitly invites PRs with empirically derived weights.

## [0.1.0] - 2026-03-26

Initial release of `riasec-co` — the first open-source package combining vocational assessment with national education data.

### Added

- **Bayesian adaptive RIASEC quiz engine** with Dirichlet posterior updates, entropy-based stopping, and information-theoretic item selection. Supports adaptive (~12 questions) and full (48 questions) modes.
- **Complete SNIES program catalog**: 30,809 programs (17,230 active) across 33 departments, 30 columns including accreditation status, propedeutic cycles, and program validity.
- **Coverage data**: 44,654 per-municipality coverage records with tuition costs across 563 municipalities.
- **Inter-institutional agreements**: 913 convenio records showing where programs are offered via partnerships.
- **48 IPIP RIASEC items** in English and Spanish (public domain, from Liao, Armstrong & Rounds 2008).
- **RIASEC→CINE field mapping**: 16 weighted associations mapping Holland types to Colombian CINE F 2013 AC broad fields.
- **Program recommendation engine** with enrollment-weighted priors, regional boost, and virtual/distance boost.
- **TypeScript package** (`riasec-co`): zero-dependency engine for Node.js and browser.
- **React components** (`riasec-co-react`): QuizWidget, ProfileChart (SVG radar), ProgramCards.
- **Python package** (`riasec-co`): Polars DataFrames, quiz engine, recommender, matplotlib plotting.
- **R package** (`riasecco`): CRAN-ready with LazyData, quiz engine, recommender, bundled .rda datasets.
- **Data pipeline**: `scripts/update-snies.ts` parses HECAA Excel exports into canonical CSV.
- **JSON schemas** for programs and enrollment data validation.
- **CI/CD**: GitHub Actions for TypeScript + Python + R testing, monthly SNIES data refresh, npm and PyPI publishing on tag.
- **Showcase plots**: RIASEC radar profile, adaptive convergence, CINE field distribution, regional comparison, top 10 recommendations.
- **Full scientific methodology** documented in METHODOLOGY.md.
- **Bilingual READMEs** in Spanish (default) and English.
