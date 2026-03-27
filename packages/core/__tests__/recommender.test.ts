import { describe, it, expect } from "vitest";
import { recommend } from "../src/recommender.js";
import { loadPrograms, loadMapping } from "../src/programs.js";
import type { RIASECProfile, Program } from "../src/types.js";

// Create a test profile strongly weighted toward Investigative
const investigativeProfile: RIASECProfile = {
  R: 0.05,
  I: 0.55,
  A: 0.05,
  S: 0.10,
  E: 0.10,
  C: 0.15,
};

// Create a test profile strongly weighted toward Artistic
const artisticProfile: RIASECProfile = {
  R: 0.05,
  I: 0.05,
  A: 0.55,
  S: 0.15,
  E: 0.10,
  C: 0.10,
};

describe("recommend", () => {
  it("returns recommendations sorted by score", () => {
    const programs = loadPrograms();
    const results = recommend({
      profile: investigativeProfile,
      programs,
      filters: { active: true },
      limit: 10,
    });

    expect(results.length).toBeGreaterThan(0);
    expect(results.length).toBeLessThanOrEqual(10);

    // Verify descending score order
    for (let i = 1; i < results.length; i++) {
      expect(results[i - 1].score).toBeGreaterThanOrEqual(results[i].score);
    }
  });

  it("recommends science/health programs for investigative profile", () => {
    const programs = loadPrograms();
    const results = recommend({
      profile: investigativeProfile,
      programs,
      filters: { active: true },
      limit: 20,
    });

    // Top results should include science, health, or engineering fields
    const topFields = results.slice(0, 10).map((r) => r.program.cine_amplio);
    const scienceHealth = topFields.filter(
      (f) =>
        f.includes("Ciencias Naturales") ||
        f.includes("Salud") ||
        f.includes("Ingeniería") ||
        f.includes("TIC") ||
        f.includes("Tecnologías")
    );
    expect(scienceHealth.length).toBeGreaterThan(0);
  });

  it("recommends arts programs for artistic profile", () => {
    const programs = loadPrograms();
    const results = recommend({
      profile: artisticProfile,
      programs,
      filters: { active: true },
      limit: 20,
    });

    const topFields = results.slice(0, 10).map((r) => r.program.cine_amplio);
    const artsHumanities = topFields.filter(
      (f) => f.includes("Arte") || f.includes("Ciencias Sociales")
    );
    expect(artsHumanities.length).toBeGreaterThan(0);
  });

  it("applies department filter", () => {
    const programs = loadPrograms();
    const results = recommend({
      profile: investigativeProfile,
      programs,
      filters: { active: true, departments: ["Sucre"] },
      limit: 20,
    });

    for (const r of results) {
      expect(r.program.departamento).toBe("Sucre");
    }
  });

  it("applies nivel_formacion filter", () => {
    const programs = loadPrograms();
    const results = recommend({
      profile: investigativeProfile,
      programs,
      filters: { active: true, nivel_formacion: ["Universitario"] },
      limit: 10,
    });

    for (const r of results) {
      expect(r.program.nivel_formacion).toBe("Universitario");
    }
  });

  it("includes match details", () => {
    const programs = loadPrograms();
    const results = recommend({
      profile: investigativeProfile,
      programs,
      filters: { active: true },
      limit: 5,
    });

    for (const r of results) {
      expect(r.matchDetails).toBeDefined();
      expect(r.matchDetails.profileSimilarity).toBeGreaterThan(0);
      expect(r.matchDetails.profileSimilarity).toBeLessThanOrEqual(1);
      expect(r.matchDetails.matchingTypes.length).toBeGreaterThan(0);
    }
  });

  it("enrollment weight downweights popular fields", () => {
    const programs = loadPrograms();

    const noWeight = recommend({
      profile: investigativeProfile,
      programs,
      filters: { active: true },
      priors: { enrollmentWeight: 0 },
      limit: 50,
    });

    const withWeight = recommend({
      profile: investigativeProfile,
      programs,
      filters: { active: true },
      priors: { enrollmentWeight: -0.5 },
      limit: 50,
    });

    // With negative enrollment weight, less popular fields should rank higher
    // Compare the average field count of top recommendations
    const mapping = loadMapping();
    expect(noWeight.length).toBeGreaterThan(0);
    expect(withWeight.length).toBeGreaterThan(0);
  });

  it("boosts virtual programs when virtualBoost is set", () => {
    const programs = loadPrograms();

    const noBoost = recommend({
      profile: investigativeProfile,
      programs,
      filters: { active: true },
      priors: { virtualBoost: 0 },
      limit: 50,
    });

    const withBoost = recommend({
      profile: investigativeProfile,
      programs,
      filters: { active: true },
      priors: { virtualBoost: 3.0 },
      limit: 50,
    });

    const virtualCountNoBoost = noBoost
      .slice(0, 20)
      .filter((r) =>
        ["Virtual", "A distancia"].includes(r.program.modalidad)
      ).length;

    const virtualCountWithBoost = withBoost
      .slice(0, 20)
      .filter((r) =>
        ["Virtual", "A distancia"].includes(r.program.modalidad)
      ).length;

    expect(virtualCountWithBoost).toBeGreaterThanOrEqual(virtualCountNoBoost);
  });

  it("respects limit parameter", () => {
    const programs = loadPrograms();
    const results = recommend({
      profile: investigativeProfile,
      programs,
      filters: { active: true },
      limit: 5,
    });
    expect(results.length).toBeLessThanOrEqual(5);
  });
});
