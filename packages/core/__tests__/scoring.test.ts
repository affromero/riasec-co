import { describe, it, expect } from "vitest";
import {
  uniformPrior,
  updateAlpha,
  posteriorMean,
  entropy,
  confidence,
  cosineSimilarity,
  klDivergence,
  expectedInfoGain,
  MAX_ENTROPY,
} from "../src/scoring.js";
import { RIASEC_TYPES } from "../src/types.js";

describe("uniformPrior", () => {
  it("creates equal alpha=1 for all types", () => {
    const prior = uniformPrior();
    for (const t of RIASEC_TYPES) {
      expect(prior[t]).toBe(1);
    }
  });
});

describe("updateAlpha", () => {
  it("increases alpha for the target type on positive-keyed response", () => {
    const prior = uniformPrior();
    const updated = updateAlpha(prior, "I", 5, "+");
    expect(updated.I).toBe(2); // 1 + (5-1)/4 = 2
    expect(updated.R).toBe(1); // unchanged
  });

  it("handles negative-keyed items by reversing response", () => {
    const prior = uniformPrior();
    const updated = updateAlpha(prior, "I", 1, "-");
    // keyed "-", response 1 → normalized = (5-1)/4 = 1.0
    expect(updated.I).toBe(2);
  });

  it("neutral response (3) adds 0.5 for positive-keyed", () => {
    const prior = uniformPrior();
    const updated = updateAlpha(prior, "R", 3, "+");
    expect(updated.R).toBe(1.5); // 1 + (3-1)/4 = 1.5
  });

  it("lowest response (1) adds 0 for positive-keyed", () => {
    const prior = uniformPrior();
    const updated = updateAlpha(prior, "R", 1, "+");
    expect(updated.R).toBe(1); // 1 + 0 = 1
  });

  it("does not mutate the original alpha", () => {
    const prior = uniformPrior();
    updateAlpha(prior, "A", 5, "+");
    expect(prior.A).toBe(1);
  });
});

describe("posteriorMean", () => {
  it("returns uniform distribution for uniform prior", () => {
    const mean = posteriorMean(uniformPrior());
    for (const t of RIASEC_TYPES) {
      expect(mean[t]).toBeCloseTo(1 / 6, 5);
    }
  });

  it("sums to 1", () => {
    const alpha = updateAlpha(
      updateAlpha(uniformPrior(), "I", 5, "+"),
      "A",
      4,
      "+"
    );
    const mean = posteriorMean(alpha);
    const sum = RIASEC_TYPES.reduce((s, t) => s + mean[t], 0);
    expect(sum).toBeCloseTo(1, 10);
  });

  it("gives highest probability to most-updated type", () => {
    let alpha = uniformPrior();
    alpha = updateAlpha(alpha, "I", 5, "+");
    alpha = updateAlpha(alpha, "I", 5, "+");
    const mean = posteriorMean(alpha);
    for (const t of RIASEC_TYPES) {
      if (t !== "I") {
        expect(mean.I).toBeGreaterThan(mean[t]);
      }
    }
  });
});

describe("entropy", () => {
  it("is maximal for uniform prior", () => {
    expect(entropy(uniformPrior())).toBeCloseTo(MAX_ENTROPY, 5);
  });

  it("decreases after evidence is added", () => {
    const prior = uniformPrior();
    const updated = updateAlpha(prior, "I", 5, "+");
    expect(entropy(updated)).toBeLessThan(entropy(prior));
  });

  it("approaches 0 for concentrated distribution", () => {
    let alpha = uniformPrior();
    for (let i = 0; i < 50; i++) {
      alpha = updateAlpha(alpha, "R", 5, "+");
    }
    expect(entropy(alpha)).toBeLessThan(1.0);
  });
});

describe("confidence", () => {
  it("is 0 for uniform prior", () => {
    expect(confidence(uniformPrior())).toBeCloseTo(0, 5);
  });

  it("increases with evidence", () => {
    const prior = uniformPrior();
    const updated = updateAlpha(prior, "E", 5, "+");
    expect(confidence(updated)).toBeGreaterThan(confidence(prior));
  });

  it("is between 0 and 1", () => {
    let alpha = uniformPrior();
    for (let i = 0; i < 10; i++) {
      alpha = updateAlpha(alpha, "S", 5, "+");
      const c = confidence(alpha);
      expect(c).toBeGreaterThanOrEqual(0);
      expect(c).toBeLessThanOrEqual(1);
    }
  });
});

describe("cosineSimilarity", () => {
  it("returns 1 for identical profiles", () => {
    const profile = posteriorMean(
      updateAlpha(uniformPrior(), "I", 5, "+")
    );
    expect(cosineSimilarity(profile, profile)).toBeCloseTo(1, 10);
  });

  it("returns a lower value for different profiles", () => {
    const a = posteriorMean(updateAlpha(uniformPrior(), "R", 5, "+"));
    const b = posteriorMean(updateAlpha(uniformPrior(), "A", 5, "+"));
    expect(cosineSimilarity(a, b)).toBeLessThan(1);
  });

  it("handles orthogonal-like profiles", () => {
    // Not truly orthogonal since all have baseline, but maximally different
    const a = { R: 1, I: 0, A: 0, S: 0, E: 0, C: 0 };
    const b = { R: 0, I: 0, A: 0, S: 0, E: 0, C: 1 };
    expect(cosineSimilarity(a, b)).toBe(0);
  });
});

describe("klDivergence", () => {
  it("is 0 for identical distributions", () => {
    const p = posteriorMean(uniformPrior());
    expect(klDivergence(p, p)).toBeCloseTo(0, 10);
  });

  it("is positive for different distributions", () => {
    const p = posteriorMean(updateAlpha(uniformPrior(), "I", 5, "+"));
    const q = posteriorMean(uniformPrior());
    expect(klDivergence(p, q)).toBeGreaterThan(0);
  });
});

describe("expectedInfoGain", () => {
  it("is higher for types with lower alpha (more uncertain)", () => {
    let alpha = uniformPrior();
    // Add evidence for I, making R more uncertain relatively
    alpha = updateAlpha(alpha, "I", 5, "+");
    alpha = updateAlpha(alpha, "I", 5, "+");

    const gainR = expectedInfoGain(alpha, "R");
    const gainI = expectedInfoGain(alpha, "I");
    // R should have higher info gain since we know less about it
    expect(gainR).toBeGreaterThan(gainI);
  });
});
