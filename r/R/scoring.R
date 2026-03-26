#' Dirichlet-based Bayesian scoring for RIASEC profiles
#'
#' @name scoring
#' @keywords internal
NULL

RIASEC_TYPES <- c("R", "I", "A", "S", "E", "C")
MAX_ENTROPY <- log2(6)

#' Create a uniform Dirichlet prior
#' @return Named numeric vector with alpha=1 for each RIASEC type
#' @keywords internal
uniform_prior <- function() {
  setNames(rep(1.0, 6), RIASEC_TYPES)
}

#' Update Dirichlet alpha after observing a response
#'
#' @param alpha Named numeric vector of Dirichlet concentrations
#' @param type Character, RIASEC type (R, I, A, S, E, or C)
#' @param response Integer, Likert response (1-5)
#' @param keyed Character, "+" or "-"
#' @return Updated alpha vector
#' @keywords internal
update_alpha <- function(alpha, type, response, keyed = "+") {
  normalized <- if (keyed == "+") (response - 1) / 4 else (5 - response) / 4
  alpha[type] <- alpha[type] + normalized
  alpha
}

#' Compute posterior mean from Dirichlet alpha
#'
#' @param alpha Named numeric vector of Dirichlet concentrations
#' @return Named numeric vector (RIASEC profile, sums to 1)
#' @keywords internal
posterior_mean <- function(alpha) {
  alpha / sum(alpha)
}

#' Shannon entropy of a RIASEC profile
#'
#' @param alpha Named numeric vector of Dirichlet concentrations
#' @return Numeric entropy value
#' @keywords internal
compute_entropy <- function(alpha) {
  p <- posterior_mean(alpha)
  -sum(p * log2(p))
}

#' Confidence from Dirichlet alpha
#'
#' @param alpha Named numeric vector of Dirichlet concentrations
#' @return Numeric in [0, 1]
#' @keywords internal
compute_confidence <- function(alpha) {
  1 - compute_entropy(alpha) / MAX_ENTROPY
}

#' Cosine similarity between two RIASEC profiles
#'
#' @param a,b Named numeric vectors
#' @return Numeric in [0, 1]
#' @keywords internal
cosine_similarity <- function(a, b) {
  dot <- sum(a * b)
  denom <- sqrt(sum(a^2)) * sqrt(sum(b^2))
  if (denom == 0) 0 else dot / denom
}

#' Expected information gain for a RIASEC type
#'
#' @param alpha Named numeric vector of Dirichlet concentrations
#' @param type Character, RIASEC type
#' @return Numeric expected KL divergence
#' @keywords internal
expected_info_gain <- function(alpha, type) {
  total_kl <- 0
  for (response in c(1L, 3L, 5L)) {
    new_alpha <- update_alpha(alpha, type, response, "+")
    p <- posterior_mean(new_alpha)
    q <- posterior_mean(alpha)
    kl <- sum(p * log2(p / q))
    total_kl <- total_kl + kl / 3
  }
  total_kl
}
