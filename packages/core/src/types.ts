/** The six Holland RIASEC types */
export const RIASEC_TYPES = ["R", "I", "A", "S", "E", "C"] as const;
export type RIASECType = (typeof RIASEC_TYPES)[number];

/** A RIASEC profile: probability distribution over 6 types */
export type RIASECProfile = Record<RIASECType, number>;

/** Dirichlet concentration parameters (alpha vector) */
export type DirichletAlpha = Record<RIASECType, number>;

/** Response scale: 1-5 Likert */
export type LikertResponse = 1 | 2 | 3 | 4 | 5;

/** A single IPIP RIASEC item */
export interface Item {
  id: string;
  type: RIASECType;
  text: string;
  keyed: "+" | "-";
}

/** Item bank with metadata */
export interface ItemBank {
  meta: {
    source: string;
    scale: string;
    reference: string;
    license: string;
    response_scale: Record<string, string>;
    types: Record<RIASECType, string>;
  };
  items: Item[];
}

/** A recorded answer */
export interface Answer {
  itemId: string;
  type: RIASECType;
  response: LikertResponse;
  keyed: "+" | "-";
}

/** Quiz configuration */
export interface QuizConfig {
  /** Language for item text */
  language: "en" | "es";
  /** Quiz mode: adaptive (entropy-based stopping) or full (all 48 items) */
  mode: "adaptive" | "full";
  /** Entropy threshold for adaptive stopping (lower = more questions). Default: 1.5 */
  entropyThreshold?: number;
  /** Maximum questions in adaptive mode. Default: 24 */
  maxQuestions?: number;
  /** Minimum questions in adaptive mode. Default: 12 */
  minQuestions?: number;
}

/** Quiz progress info */
export interface QuizProgress {
  answered: number;
  total: number;
  estimatedRemaining: number;
  confidence: number;
  entropy: number;
}

/** A SNIES program record (canonical CSV row) */
export interface Program {
  codigo_snies: number;
  nombre_programa: string;
  codigo_institucion: string;
  nombre_institucion: string;
  estado: "Activo" | "Inactivo";
  estado_institucion: string;
  caracter_academico: string;
  sector: string;
  nivel_academico: string;
  nivel_formacion: string;
  modalidad: string;
  titulo_otorgado: string;
  cine_amplio: string;
  cine_especifico: string;
  cine_detallado: string;
  area_conocimiento: string;
  nucleo_conocimiento: string;
  departamento: string;
  municipio: string;
  creditos: number | null;
  periodos_duracion: number | null;
  periodicidad: string | null;
  costo_matricula: number | null;
  en_convenio: string | null;
}

/** RIASEC → CINE field mapping entry */
export interface FieldMapping {
  cine_amplio: string;
  weight: number;
}

/** Full mapping for one RIASEC type */
export interface TypeMapping {
  name: string;
  name_es: string;
  description: string;
  fields: FieldMapping[];
}

/** Recommendation config */
export interface RecommendConfig {
  profile: RIASECProfile;
  programs: Program[];
  mapping?: Record<RIASECType, TypeMapping>;
  filters?: ProgramFilters;
  priors?: PriorWeights;
  limit?: number;
}

/** Filters for program recommendations */
export interface ProgramFilters {
  departments?: string[];
  active?: boolean;
  nivel_formacion?: string[];
  modalidad?: string[];
  sector?: string[];
}

/** Prior weights for recommendation scoring */
export interface PriorWeights {
  /** Weight for enrollment-based adjustment. Negative = downweight popular fields. Default: -0.3 */
  enrollmentWeight?: number;
  /** Boost for programs in specified departments. Default: 1.0 */
  regionalBoost?: number;
  /** Boost for virtual/distance programs. Default: 1.0 */
  virtualBoost?: number;
}

/** A single program recommendation with score */
export interface Recommendation {
  program: Program;
  score: number;
  matchDetails: {
    profileSimilarity: number;
    priorAdjustment: number;
    matchingTypes: RIASECType[];
  };
}
