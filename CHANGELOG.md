# Changelog

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
- **TypeScript package** (`@riasec-co/core`): zero-dependency engine for Node.js and browser.
- **React components** (`@riasec-co/react`): QuizWidget, ProfileChart (SVG radar), ProgramCards.
- **Python package** (`riasec-co`): Polars DataFrames, quiz engine, recommender, matplotlib plotting.
- **R package** (`riasecco`): CRAN-ready with LazyData, quiz engine, recommender, bundled .rda datasets.
- **Data pipeline**: `scripts/update-snies.ts` parses HECAA Excel exports into canonical CSV.
- **JSON schemas** for programs and enrollment data validation.
- **CI/CD**: GitHub Actions for TypeScript + Python + R testing, monthly SNIES data refresh, npm and PyPI publishing on tag.
- **Showcase plots**: RIASEC radar profile, adaptive convergence, CINE field distribution, regional comparison, top 10 recommendations.
- **Full scientific methodology** documented in METHODOLOGY.md.
- **Bilingual READMEs** in Spanish (default) and English.
