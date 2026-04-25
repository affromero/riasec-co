# Changelog

## [Unreleased]

### Fixed

- `data/canonical/items_es.json`: corrected the Spanish-version reference. The previous citation ("Armstrong, P. I., Allison, W., & Rounds, J. (2020). Alternate Forms Public Domain RIASEC Markers") was wrong on both authors and year. The actual paper that adapted the IPIP-BIM scale to Spanish (Río de la Plata variant) is Cupani, M., Moran, V. E., Azpilicueta, A. E., & Piccolo, N. V. (2019), *Electronic Journal of Research in Educational Psychology*, 17(2), 359-382 (DOI 10.25115/ejrep.v17i48.2136).

### Added

- `reference_doi` and `reference_url` fields on `items_es.json` and `items_en.json` so consumers can verify the source citation without manual lookup.
- `validation_status`, `contribution_invitation`, and `references` fields on `mapping.json`. The mapping is author-curated based on Holland (1997) and the SNIES CINE taxonomy; it has not been independently psychometrically validated against external criteria such as O*NET RIASEC interest profiles. PRs with empirically derived weights are welcome.

### Changed

- `data/canonical/mapping.json`'s `source` description now reads "Author-curated weighted mapping..." (previously "Expert mapping...") for accuracy and transparency.

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
