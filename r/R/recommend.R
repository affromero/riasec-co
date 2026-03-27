#' Recommend programs based on RIASEC profile
#'
#' Matches a student's RIASEC profile against SNIES programs using
#' the RIASEC-to-CINE field mapping. Supports enrollment-weighted
#' priors that surface hidden-gem programs.
#'
#' @param profile Named numeric vector: RIASEC profile (sums to 1)
#' @param programs Data frame of programs (default: \code{riasecco::programs})
#' @param mapping Data frame of RIASEC-CINE mapping (default: built-in)
#' @param departments Character vector: filter by departments (optional)
#' @param active_only Logical: filter to active programs only. Default: TRUE
#' @param nivel_formacion Character vector: filter by education level (optional)
#' @param enrollment_weight Numeric: enrollment-based prior weight.
#'   Negative values downweight popular fields. Default: -0.3
#' @param regional_boost Numeric: boost for programs in specified departments.
#'   Default: 1.0
#' @param virtual_boost Numeric: boost for virtual/distance programs.
#'   Default: 1.0
#' @param limit Integer: maximum recommendations. Default: 20
#' @return Data frame with program data plus score, similarity, matching_types
#' @export
#' @examples
#' profile <- c(R = 0.05, I = 0.55, A = 0.05, S = 0.10, E = 0.10, C = 0.15)
#' results <- recommend(profile, departments = "Sucre", limit = 10)
#' head(results[, c("nombre_programa", "nombre_institucion", "score")])
recommend <- function(profile,
                      programs = NULL,
                      mapping = NULL,
                      departments = NULL,
                      active_only = TRUE,
                      nivel_formacion = NULL,
                      enrollment_weight = -0.3,
                      regional_boost = 1.0,
                      virtual_boost = 1.0,
                      limit = 20L) {
  if (is.null(programs)) {
    programs <- riasecco::programs
  }
  if (is.null(mapping)) {
    mapping <- riasecco::riasec_mapping
  }

  df <- programs

  # Apply filters
  if (active_only) df <- df[df$estado == "Activo", ]
  if (!is.null(departments)) df <- df[df$departamento %in% departments, ]
  if (!is.null(nivel_formacion)) df <- df[df$nivel_formacion %in% nivel_formacion, ]

  if (nrow(df) == 0) return(df)

  # Pre-compute field profiles
  unique_fields <- unique(df$cine_amplio)
  field_profiles <- lapply(setNames(unique_fields, unique_fields), function(field) {
    fp <- setNames(rep(0, 6), RIASEC_TYPES)
    for (i in seq_len(nrow(mapping))) {
      if (mapping$cine_amplio[i] == field) {
        fp[mapping$riasec_type[i]] <- mapping$weight[i]
      }
    }
    fp
  })

  # Field counts for enrollment priors
  all_active <- programs[programs$estado == "Activo", ]
  total_programs <- nrow(all_active)
  field_counts <- table(all_active$cine_amplio)

  virtual_modalities <- c("Virtual", "A distancia", "Virtual-A distancia")
  regional_set <- if (!is.null(departments)) departments else character(0)

  # Score each program
  scores <- numeric(nrow(df))
  sims <- numeric(nrow(df))
  match_types <- character(nrow(df))

  for (i in seq_len(nrow(df))) {
    cine <- df$cine_amplio[i]
    fp <- field_profiles[[cine]]

    if (is.null(fp) || all(fp == 0)) next

    sim <- cosine_similarity(profile, fp)
    if (sim == 0) next

    # Enrollment factor
    fc <- as.numeric(field_counts[cine])
    if (is.na(fc)) fc <- 1
    enrollment_factor <- 1 + enrollment_weight * log(total_programs / fc)

    # Regional factor
    is_regional <- if (df$departamento[i] %in% regional_set) 1 else 0
    regional_factor <- 1 + regional_boost * is_regional

    # Virtual factor
    is_virtual <- if (df$modalidad[i] %in% virtual_modalities) 1 else 0
    virtual_factor <- 1 + virtual_boost * is_virtual

    scores[i] <- sim * enrollment_factor * regional_factor * virtual_factor
    sims[i] <- sim
    match_types[i] <- paste(RIASEC_TYPES[fp > 0], collapse = ",")
  }

  df$score <- scores
  df$similarity <- sims
  df$matching_types <- match_types

  # Sort, deduplicate, limit
  df <- df[order(-df$score), ]
  df <- df[!duplicated(df$codigo_snies), ]
  df <- head(df, limit)
  rownames(df) <- NULL

  df
}
