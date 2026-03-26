export { createQuiz } from "./quiz.js";
export type { Quiz } from "./quiz.js";

export {
  uniformPrior,
  updateAlpha,
  posteriorMean,
  entropy,
  confidence,
  cosineSimilarity,
  klDivergence,
  expectedInfoGain,
  MAX_ENTROPY,
} from "./scoring.js";

export { loadItems, getItemsByType } from "./items.js";
export {
  loadPrograms,
  loadMapping,
  getCINEFields,
  getDepartments,
} from "./programs.js";

export { recommend } from "./recommender.js";

export {
  RIASEC_TYPES,
  type RIASECType,
  type RIASECProfile,
  type DirichletAlpha,
  type LikertResponse,
  type Item,
  type ItemBank,
  type Answer,
  type QuizConfig,
  type QuizProgress,
  type Program,
  type Cobertura,
  type Convenio,
  type FieldMapping,
  type TypeMapping,
  type RecommendConfig,
  type ProgramFilters,
  type PriorWeights,
  type Recommendation,
} from "./types.js";
