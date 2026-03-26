/**
 * recommender.ts — Program recommendation engine
 *
 * Matches a student's RIASEC profile to SNIES programs using
 * the RIASEC → CINE field mapping. Supports enrollment-weighted
 * priors that surface hidden-gem programs.
 */

import { cosineSimilarity } from "./scoring.js";
import { loadMapping } from "./programs.js";
import { RIASEC_TYPES } from "./types.js";
import type {
  RIASECProfile,
  RIASECType,
  Program,
  TypeMapping,
  RecommendConfig,
  ProgramFilters,
  Recommendation,
} from "./types.js";

const VIRTUAL_MODALITIES = new Set([
  "Virtual",
  "A distancia",
  "Virtual-A distancia",
]);

/**
 * Build a RIASEC profile vector for a given CINE broad field,
 * based on the mapping weights.
 */
function fieldToProfile(
  cineAmplio: string,
  mapping: Record<RIASECType, TypeMapping>
): RIASECProfile {
  const profile: RIASECProfile = { R: 0, I: 0, A: 0, S: 0, E: 0, C: 0 };

  for (const type of RIASEC_TYPES) {
    const entry = mapping[type];
    for (const field of entry.fields) {
      if (field.cine_amplio === cineAmplio) {
        profile[type] = field.weight;
      }
    }
  }

  return profile;
}

/** Apply filters to a program list */
function applyFilters(programs: Program[], filters?: ProgramFilters): Program[] {
  if (!filters) return programs;

  let result = programs;

  if (filters.active !== undefined) {
    const status = filters.active ? "Activo" : "Inactivo";
    result = result.filter((p) => p.estado === status);
  }

  if (filters.departments?.length) {
    const depts = new Set(filters.departments);
    result = result.filter((p) => depts.has(p.departamento));
  }

  if (filters.nivel_formacion?.length) {
    const niveles = new Set(filters.nivel_formacion);
    result = result.filter((p) => niveles.has(p.nivel_formacion));
  }

  if (filters.modalidad?.length) {
    const mods = new Set(filters.modalidad);
    result = result.filter((p) => mods.has(p.modalidad));
  }

  if (filters.sector?.length) {
    const sectors = new Set(filters.sector);
    result = result.filter((p) => sectors.has(p.sector));
  }

  return result;
}

/**
 * Compute program counts per CINE broad field (for enrollment-based priors).
 * Uses program count as a proxy for enrollment when actual enrollment data
 * is not available.
 */
function computeFieldCounts(programs: Program[]): Map<string, number> {
  const counts = new Map<string, number>();
  for (const p of programs) {
    const field = p.cine_amplio;
    if (field) {
      counts.set(field, (counts.get(field) ?? 0) + 1);
    }
  }
  return counts;
}

/**
 * Recommend programs based on RIASEC profile.
 *
 * score(program) = similarity(student_profile, program_cine_vector)
 *               × prior(program)
 *
 * prior(program) = base
 *               × (1 + enrollmentWeight × log(national / field_count))
 *               × (1 + regionalBoost × isInRegion)
 *               × (1 + virtualBoost × isVirtual)
 */
export function recommend(config: RecommendConfig): Recommendation[] {
  const {
    profile,
    programs,
    filters,
    limit = 20,
  } = config;

  const mapping = config.mapping ?? loadMapping();
  const priors = {
    enrollmentWeight: config.priors?.enrollmentWeight ?? -0.3,
    regionalBoost: config.priors?.regionalBoost ?? 1.0,
    virtualBoost: config.priors?.virtualBoost ?? 1.0,
  };

  const filtered = applyFilters(programs, filters);
  const fieldCounts = computeFieldCounts(programs); // use full dataset for counts
  const totalPrograms = programs.filter((p) => p.estado === "Activo").length;

  // Pre-compute field profiles
  const fieldProfileCache = new Map<string, RIASECProfile>();
  for (const field of fieldCounts.keys()) {
    fieldProfileCache.set(field, fieldToProfile(field, mapping));
  }

  const regionalDepts = filters?.departments
    ? new Set(filters.departments)
    : null;

  const results: Recommendation[] = [];

  for (const program of filtered) {
    const fieldProfile = fieldProfileCache.get(program.cine_amplio);
    if (!fieldProfile) continue;

    // Profile similarity (cosine)
    const similarity = cosineSimilarity(profile, fieldProfile);
    if (similarity === 0) continue;

    // Enrollment-based prior
    const fieldCount = fieldCounts.get(program.cine_amplio) ?? 1;
    const enrollmentFactor =
      1 + priors.enrollmentWeight * Math.log(totalPrograms / fieldCount);

    // Regional boost
    const isRegional = regionalDepts?.has(program.departamento) ? 1 : 0;
    const regionalFactor = 1 + priors.regionalBoost * isRegional;

    // Virtual boost
    const isVirtual = VIRTUAL_MODALITIES.has(program.modalidad) ? 1 : 0;
    const virtualFactor = 1 + priors.virtualBoost * isVirtual;

    const priorAdjustment = enrollmentFactor * regionalFactor * virtualFactor;
    const score = similarity * priorAdjustment;

    // Find which RIASEC types match this field
    const matchingTypes = RIASEC_TYPES.filter(
      (t) => fieldProfile[t] > 0
    );

    results.push({
      program,
      score,
      matchDetails: {
        profileSimilarity: similarity,
        priorAdjustment,
        matchingTypes,
      },
    });
  }

  // Sort by score descending, deduplicate by program name + institution
  results.sort((a, b) => b.score - a.score);

  // Deduplicate: keep highest-scoring entry per unique program
  const seen = new Set<string>();
  const deduped: Recommendation[] = [];
  for (const r of results) {
    const key = `${r.program.codigo_snies}`;
    if (!seen.has(key)) {
      seen.add(key);
      deduped.push(r);
    }
  }

  return deduped.slice(0, limit);
}
