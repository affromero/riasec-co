test_that("quiz creates with defaults", {
  skip_if_not(file.exists(
    system.file("extdata", "items_en.json", package = "riasecco")
  ), "Package not installed with extdata")

  quiz <- create_quiz(language = "en")
  expect_false(is_complete(quiz))
  expect_length(quiz$answers, 0)
})

test_that("quiz returns a question", {
  skip_if_not(file.exists(
    system.file("extdata", "items_en.json", package = "riasecco")
  ), "Package not installed with extdata")

  quiz <- create_quiz(language = "en")
  q <- next_question(quiz)
  expect_type(q, "list")
  expect_true(q$type %in% c("R", "I", "A", "S", "E", "C"))
})

test_that("quiz records answers", {
  skip_if_not(file.exists(
    system.file("extdata", "items_en.json", package = "riasecco")
  ), "Package not installed with extdata")

  quiz <- create_quiz(language = "en")
  q <- next_question(quiz)
  answer(quiz, q$id, 5L)
  expect_length(quiz$answers, 1)
  prof <- profile(quiz)
  expect_gt(prof[[q$type]], 1/6)
})

test_that("quiz rejects duplicate answer", {
  skip_if_not(file.exists(
    system.file("extdata", "items_en.json", package = "riasecco")
  ), "Package not installed with extdata")

  quiz <- create_quiz(language = "en")
  q <- next_question(quiz)
  answer(quiz, q$id, 3L)
  expect_error(answer(quiz, q$id, 4L), "already answered")
})

test_that("quiz rejects invalid response", {
  skip_if_not(file.exists(
    system.file("extdata", "items_en.json", package = "riasecco")
  ), "Package not installed with extdata")

  quiz <- create_quiz(language = "en")
  q <- next_question(quiz)
  expect_error(answer(quiz, q$id, 0L), "Invalid response")
  expect_error(answer(quiz, q$id, 6L), "Invalid response")
})

test_that("full mode asks all 48 questions", {
  skip_if_not(file.exists(
    system.file("extdata", "items_en.json", package = "riasecco")
  ), "Package not installed with extdata")

  quiz <- create_quiz(language = "en", mode = "full")
  count <- 0
  while (!is_complete(quiz)) {
    q <- next_question(quiz)
    if (is.null(q)) break
    answer(quiz, q$id, 3L)
    count <- count + 1
  }
  expect_equal(count, 48)
})
