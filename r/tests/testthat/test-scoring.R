test_that("uniform prior has equal values", {
  alpha <- riasecco:::uniform_prior()
  expect_length(alpha, 6)
  expect_true(all(alpha == 1))
})

test_that("update_alpha increases target type", {
  alpha <- riasecco:::uniform_prior()
  updated <- riasecco:::update_alpha(alpha, "I", 5L, "+")
  expect_equal(updated[["I"]], 2)  # 1 + (5-1)/4
  expect_equal(updated[["R"]], 1)  # unchanged
})

test_that("posterior_mean is uniform for uniform prior", {
  alpha <- riasecco:::uniform_prior()
  mean <- riasecco:::posterior_mean(alpha)
  expect_equal(unname(mean), rep(1/6, 6), tolerance = 1e-10)
})

test_that("posterior_mean sums to 1", {
  alpha <- riasecco:::uniform_prior()
  alpha <- riasecco:::update_alpha(alpha, "I", 5L, "+")
  alpha <- riasecco:::update_alpha(alpha, "A", 4L, "+")
  expect_equal(sum(riasecco:::posterior_mean(alpha)), 1, tolerance = 1e-10)
})

test_that("entropy is maximal for uniform prior", {
  alpha <- riasecco:::uniform_prior()
  expect_equal(riasecco:::compute_entropy(alpha),
               riasecco:::MAX_ENTROPY, tolerance = 1e-10)
})

test_that("entropy decreases with evidence", {
  prior <- riasecco:::uniform_prior()
  updated <- riasecco:::update_alpha(prior, "I", 5L, "+")
  expect_lt(riasecco:::compute_entropy(updated),
            riasecco:::compute_entropy(prior))
})

test_that("confidence starts at 0", {
  alpha <- riasecco:::uniform_prior()
  expect_equal(riasecco:::compute_confidence(alpha), 0, tolerance = 1e-10)
})

test_that("cosine similarity is 1 for identical profiles", {
  alpha <- riasecco:::update_alpha(riasecco:::uniform_prior(), "I", 5L, "+")
  p <- riasecco:::posterior_mean(alpha)
  expect_equal(riasecco:::cosine_similarity(p, p), 1, tolerance = 1e-10)
})
