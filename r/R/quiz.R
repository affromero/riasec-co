#' Create a RIASEC quiz
#'
#' Creates a new Bayesian adaptive RIASEC quiz engine.
#'
#' @param language Character: "en" or "es". Default: "es"
#' @param mode Character: "adaptive" or "full". Default: "adaptive"
#' @param entropy_threshold Numeric: entropy threshold for adaptive stopping.
#'   Default: 1.5
#' @param max_questions Integer: maximum questions in adaptive mode. Default: 24
#' @param min_questions Integer: minimum questions in adaptive mode. Default: 12
#' @return A quiz object (environment)
#' @export
#' @examples
#' quiz <- create_quiz(language = "es")
#' q <- next_question(quiz)
#' quiz <- answer(quiz, q$id, 4L)
#' profile(quiz)
create_quiz <- function(language = "es",
                        mode = "adaptive",
                        entropy_threshold = 1.5,
                        max_questions = 24L,
                        min_questions = 12L) {
  items <- load_items(language)
  alpha <- uniform_prior()
  answered <- character(0)
  answers <- list()

  quiz <- new.env(parent = emptyenv())
  quiz$items <- items
  quiz$alpha <- alpha
  quiz$answered <- answered
  quiz$answers <- answers
  quiz$mode <- mode
  quiz$entropy_threshold <- entropy_threshold
  quiz$max_questions <- as.integer(max_questions)
  quiz$min_questions <- as.integer(min_questions)

  class(quiz) <- "riasec_quiz"
  quiz
}

#' Get the next question
#'
#' @param quiz A quiz object created by \code{create_quiz}
#' @return A list with id, type, text, keyed; or NULL if quiz is complete
#' @export
next_question <- function(quiz) {
  if (is_complete(quiz)) return(NULL)

  remaining_idx <- which(!quiz$items$id %in% quiz$answered)
  if (length(remaining_idx) == 0) return(NULL)

  if (quiz$mode == "full") {
    idx <- remaining_idx[1]
  } else {
    # Adaptive: pick item with highest expected info gain
    best_idx <- remaining_idx[1]
    best_gain <- -Inf
    for (i in remaining_idx) {
      gain <- expected_info_gain(quiz$alpha, quiz$items$type[i])
      if (gain > best_gain) {
        best_gain <- gain
        best_idx <- i
      }
    }
    idx <- best_idx
  }

  list(
    id = quiz$items$id[idx],
    type = quiz$items$type[idx],
    text = quiz$items$text[idx],
    keyed = quiz$items$keyed[idx]
  )
}

#' Record an answer
#'
#' @param quiz A quiz object
#' @param item_id Character: item ID
#' @param response Integer: Likert response (1-5)
#' @return The updated quiz object (modified in place)
#' @export
answer <- function(quiz, item_id, response) {
  idx <- match(item_id, quiz$items$id)
  if (is.na(idx)) stop("Unknown item: ", item_id)
  if (item_id %in% quiz$answered) stop("Item already answered: ", item_id)
  if (response < 1 || response > 5) stop("Invalid response: ", response)

  quiz$answered <- c(quiz$answered, item_id)
  quiz$alpha <- update_alpha(
    quiz$alpha,
    quiz$items$type[idx],
    response,
    quiz$items$keyed[idx]
  )
  quiz$answers <- c(quiz$answers, list(list(
    item_id = item_id,
    type = quiz$items$type[idx],
    response = response,
    keyed = quiz$items$keyed[idx]
  )))

  invisible(quiz)
}

#' Check if quiz is complete
#'
#' @param quiz A quiz object
#' @return Logical
#' @export
is_complete <- function(quiz) {
  n <- length(quiz$answered)
  if (quiz$mode == "full") return(n >= nrow(quiz$items))
  if (n >= quiz$max_questions) return(TRUE)
  if (n < quiz$min_questions) return(FALSE)
  compute_entropy(quiz$alpha) < quiz$entropy_threshold
}

#' Get current RIASEC profile
#'
#' @param quiz A quiz object
#' @return Named numeric vector (sums to 1)
#' @export
profile <- function(quiz) {
  posterior_mean(quiz$alpha)
}

#' Get quiz progress
#'
#' @param quiz A quiz object
#' @return A list with answered, total, estimated_remaining, confidence, entropy
#' @export
progress <- function(quiz) {
  n <- length(quiz$answered)
  total <- if (quiz$mode == "full") nrow(quiz$items) else quiz$max_questions
  ent <- compute_entropy(quiz$alpha)
  conf <- compute_confidence(quiz$alpha)

  remaining <- if (quiz$mode == "full") {
    nrow(quiz$items) - n
  } else if (n < quiz$min_questions) {
    quiz$min_questions - n
  } else if (ent < quiz$entropy_threshold) {
    0L
  } else {
    min(quiz$max_questions - n, ceiling((ent - quiz$entropy_threshold) * 8))
  }

  list(
    answered = n,
    total = total,
    estimated_remaining = remaining,
    confidence = conf,
    entropy = ent
  )
}

#' Get top RIASEC types
#'
#' @param quiz A quiz object
#' @param n Integer: how many top types to return. Default: 3
#' @return Character vector of top RIASEC types
#' @export
top_types <- function(quiz, n = 3L) {
  prof <- profile(quiz)
  names(sort(prof, decreasing = TRUE))[seq_len(min(n, 6))]
}
