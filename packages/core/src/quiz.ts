/**
 * quiz.ts — Bayesian adaptive RIASEC quiz engine
 *
 * Implements an adaptive testing engine that selects the most informative
 * question at each step using expected information gain (KL divergence).
 * Stops when posterior entropy drops below a configurable threshold.
 */

import {
  uniformPrior,
  updateAlpha,
  posteriorMean,
  entropy,
  confidence,
  expectedInfoGain,
} from "./scoring.js";
import { loadItems } from "./items.js";
import type {
  Item,
  Answer,
  QuizConfig,
  QuizProgress,
  RIASECProfile,
  DirichletAlpha,
  LikertResponse,
  RIASECType,
} from "./types.js";

const DEFAULT_CONFIG: Required<QuizConfig> = {
  language: "es",
  mode: "adaptive",
  entropyThreshold: 1.5,
  maxQuestions: 24,
  minQuestions: 12,
};

export interface Quiz {
  /** Get the next question to ask. Returns null if quiz is complete. */
  nextQuestion(): Item | null;
  /** Record an answer */
  answer(itemId: string, response: LikertResponse): void;
  /** Check if the quiz should stop */
  isComplete(): boolean;
  /** Get current progress */
  progress(): QuizProgress;
  /** Get current RIASEC profile (posterior mean) */
  profile(): RIASECProfile;
  /** Get current Dirichlet alpha parameters */
  alpha(): DirichletAlpha;
  /** Get all recorded answers */
  answers(): Answer[];
  /** Get the top N RIASEC types */
  topTypes(n?: number): RIASECType[];
}

/** Create a new quiz instance */
export function createQuiz(config?: Partial<QuizConfig>): Quiz {
  const cfg = { ...DEFAULT_CONFIG, ...config };
  const bank = loadItems(cfg.language);
  const allItems = [...bank.items];

  let alpha = uniformPrior();
  const answeredItems = new Set<string>();
  const recordedAnswers: Answer[] = [];

  function nextQuestion(): Item | null {
    if (isComplete()) return null;

    const remaining = allItems.filter((i) => !answeredItems.has(i.id));
    if (remaining.length === 0) return null;

    if (cfg.mode === "full") {
      // In full mode, return items in order
      return remaining[0];
    }

    // Adaptive mode: pick the item with highest expected information gain
    let bestItem = remaining[0];
    let bestGain = -Infinity;

    for (const item of remaining) {
      const gain = expectedInfoGain(alpha, item.type);
      if (gain > bestGain) {
        bestGain = gain;
        bestItem = item;
      }
    }

    return bestItem;
  }

  function answer(itemId: string, response: LikertResponse): void {
    const item = allItems.find((i) => i.id === itemId);
    if (!item) throw new Error(`Unknown item: ${itemId}`);
    if (answeredItems.has(itemId)) throw new Error(`Item already answered: ${itemId}`);
    if (response < 1 || response > 5) throw new Error(`Invalid response: ${response}`);

    answeredItems.add(itemId);
    alpha = updateAlpha(alpha, item.type, response, item.keyed);
    recordedAnswers.push({
      itemId,
      type: item.type,
      response,
      keyed: item.keyed,
    });
  }

  function isComplete(): boolean {
    const answered = answeredItems.size;

    if (cfg.mode === "full") {
      return answered >= allItems.length;
    }

    // Adaptive: stop when we have enough data and entropy is low enough
    if (answered >= cfg.maxQuestions) return true;
    if (answered < cfg.minQuestions) return false;

    return entropy(alpha) < cfg.entropyThreshold;
  }

  function progress(): QuizProgress {
    const answered = answeredItems.size;
    const total = cfg.mode === "full" ? allItems.length : cfg.maxQuestions;
    const currentEntropy = entropy(alpha);
    const conf = confidence(alpha);

    let estimatedRemaining: number;
    if (cfg.mode === "full") {
      estimatedRemaining = allItems.length - answered;
    } else if (answered < cfg.minQuestions) {
      estimatedRemaining = cfg.minQuestions - answered;
    } else if (currentEntropy < cfg.entropyThreshold) {
      estimatedRemaining = 0;
    } else {
      // Rough estimate based on entropy decay rate
      estimatedRemaining = Math.min(
        cfg.maxQuestions - answered,
        Math.ceil((currentEntropy - cfg.entropyThreshold) * 8)
      );
    }

    return {
      answered,
      total,
      estimatedRemaining,
      confidence: conf,
      entropy: currentEntropy,
    };
  }

  function getProfile(): RIASECProfile {
    return posteriorMean(alpha);
  }

  function getAlpha(): DirichletAlpha {
    return { ...alpha };
  }

  function getAnswers(): Answer[] {
    return [...recordedAnswers];
  }

  function topTypes(n: number = 3): RIASECType[] {
    const profile = getProfile();
    return (Object.entries(profile) as [RIASECType, number][])
      .sort((a, b) => b[1] - a[1])
      .slice(0, n)
      .map(([type]) => type);
  }

  return {
    nextQuestion,
    answer,
    isComplete,
    progress,
    profile: getProfile,
    alpha: getAlpha,
    answers: getAnswers,
    topTypes,
  };
}
