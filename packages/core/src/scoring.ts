/**
 * scoring.ts — Dirichlet-based Bayesian scoring for RIASEC profiles
 *
 * Uses Dirichlet distribution as conjugate prior for the categorical
 * distribution over 6 RIASEC types. Each answer updates the alpha
 * (concentration) parameters.
 */

import { RIASEC_TYPES, type RIASECType, type RIASECProfile, type DirichletAlpha, type LikertResponse } from "./types.js";

/** Create uniform Dirichlet prior: α = (1, 1, 1, 1, 1, 1) */
export function uniformPrior(): DirichletAlpha {
  return Object.fromEntries(RIASEC_TYPES.map((t) => [t, 1])) as DirichletAlpha;
}

/**
 * Update Dirichlet alpha after observing a response.
 *
 * For a positively-keyed item of type T with response r (1-5):
 *   α_T += (r - 1) / 4  (normalized to [0, 1])
 *
 * For negatively-keyed items, the response is reversed:
 *   α_T += (5 - r) / 4
 */
export function updateAlpha(
  alpha: DirichletAlpha,
  type: RIASECType,
  response: LikertResponse,
  keyed: "+" | "-"
): DirichletAlpha {
  const normalized = keyed === "+"
    ? (response - 1) / 4
    : (5 - response) / 4;

  return {
    ...alpha,
    [type]: alpha[type] + normalized,
  };
}

/**
 * Compute the posterior mean (expected profile) from Dirichlet alpha.
 * E[θ_k] = α_k / Σα
 */
export function posteriorMean(alpha: DirichletAlpha): RIASECProfile {
  const sum = alphaSum(alpha);
  return Object.fromEntries(
    RIASEC_TYPES.map((t) => [t, alpha[t] / sum])
  ) as RIASECProfile;
}

/** Sum of all alpha parameters */
export function alphaSum(alpha: DirichletAlpha): number {
  return RIASEC_TYPES.reduce((s, t) => s + alpha[t], 0);
}

/**
 * Shannon entropy of the posterior mean.
 * H = -Σ p_k log2(p_k)
 *
 * Maximum entropy (uniform) = log2(6) ≈ 2.585
 * Minimum entropy = 0 (all mass on one type)
 */
export function entropy(alpha: DirichletAlpha): number {
  const profile = posteriorMean(alpha);
  let h = 0;
  for (const t of RIASEC_TYPES) {
    const p = profile[t];
    if (p > 0) {
      h -= p * Math.log2(p);
    }
  }
  return h;
}

/** Maximum possible entropy for 6 categories */
export const MAX_ENTROPY = Math.log2(6);

/**
 * Confidence: 1 - (entropy / max_entropy)
 * 0 = uniform (no info), 1 = certain (all mass on one type)
 */
export function confidence(alpha: DirichletAlpha): number {
  return 1 - entropy(alpha) / MAX_ENTROPY;
}

/**
 * Expected information gain from asking an item of a given type.
 *
 * Approximation: items of the type with lowest alpha (most uncertain)
 * yield the most information gain. We compute the expected KL divergence
 * between the current posterior and the expected posterior after answering.
 */
export function expectedInfoGain(alpha: DirichletAlpha, type: RIASECType): number {
  const sum = alphaSum(alpha);

  // Simulate average response (response=3, neutral contribution)
  // and high response (response=5, full contribution)
  // Weight: 50% neutral, 50% positive (approximation of response distribution)
  let totalKL = 0;

  for (const response of [1, 3, 5] as LikertResponse[]) {
    const newAlpha = updateAlpha(alpha, type, response, "+");
    const kl = klDivergence(posteriorMean(newAlpha), posteriorMean(alpha));
    totalKL += kl / 3; // uniform weight over simulated responses
  }

  return totalKL;
}

/**
 * KL divergence: D_KL(P || Q) = Σ P(x) log2(P(x) / Q(x))
 */
export function klDivergence(p: RIASECProfile, q: RIASECProfile): number {
  let kl = 0;
  for (const t of RIASEC_TYPES) {
    if (p[t] > 0 && q[t] > 0) {
      kl += p[t] * Math.log2(p[t] / q[t]);
    }
  }
  return kl;
}

/**
 * Cosine similarity between two RIASEC profiles.
 * Returns value in [0, 1].
 */
export function cosineSimilarity(a: RIASECProfile, b: RIASECProfile): number {
  let dot = 0, normA = 0, normB = 0;
  for (const t of RIASEC_TYPES) {
    dot += a[t] * b[t];
    normA += a[t] * a[t];
    normB += b[t] * b[t];
  }
  const denom = Math.sqrt(normA) * Math.sqrt(normB);
  return denom === 0 ? 0 : dot / denom;
}
