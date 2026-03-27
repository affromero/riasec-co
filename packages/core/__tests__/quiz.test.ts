import { describe, it, expect } from "vitest";
import { createQuiz } from "../src/quiz.js";
import { RIASEC_TYPES } from "../src/types.js";

describe("createQuiz", () => {
  it("creates a quiz with default config", () => {
    const quiz = createQuiz({ language: "en" });
    expect(quiz.isComplete()).toBe(false);
    expect(quiz.answers()).toHaveLength(0);
  });

  it("returns a first question", () => {
    const quiz = createQuiz({ language: "en" });
    const q = quiz.nextQuestion();
    expect(q).not.toBeNull();
    expect(q!.id).toBeTruthy();
    expect(q!.text).toBeTruthy();
    expect(RIASEC_TYPES).toContain(q!.type);
  });

  it("records answers and updates profile", () => {
    const quiz = createQuiz({ language: "en" });
    const q = quiz.nextQuestion()!;

    quiz.answer(q.id, 5);

    expect(quiz.answers()).toHaveLength(1);
    expect(quiz.answers()[0].itemId).toBe(q.id);
    expect(quiz.answers()[0].response).toBe(5);

    // Profile should now favor the answered type
    const profile = quiz.profile();
    expect(profile[q.type]).toBeGreaterThan(1 / 6);
  });

  it("throws on duplicate answer", () => {
    const quiz = createQuiz({ language: "en" });
    const q = quiz.nextQuestion()!;
    quiz.answer(q.id, 3);
    expect(() => quiz.answer(q.id, 4)).toThrow("already answered");
  });

  it("throws on invalid response", () => {
    const quiz = createQuiz({ language: "en" });
    const q = quiz.nextQuestion()!;
    expect(() => quiz.answer(q.id, 0 as any)).toThrow("Invalid response");
    expect(() => quiz.answer(q.id, 6 as any)).toThrow("Invalid response");
  });

  it("throws on unknown item", () => {
    const quiz = createQuiz({ language: "en" });
    expect(() => quiz.answer("NONEXISTENT", 3)).toThrow("Unknown item");
  });

  it("reports progress correctly", () => {
    const quiz = createQuiz({ language: "en", mode: "adaptive" });
    const p0 = quiz.progress();
    expect(p0.answered).toBe(0);
    expect(p0.confidence).toBeCloseTo(0);
    expect(p0.entropy).toBeGreaterThan(2);

    const q = quiz.nextQuestion()!;
    quiz.answer(q.id, 5);

    const p1 = quiz.progress();
    expect(p1.answered).toBe(1);
    expect(p1.confidence).toBeGreaterThan(0);
  });
});

describe("quiz adaptive mode", () => {
  it("stops after enough questions when pattern is clear", () => {
    const quiz = createQuiz({
      language: "en",
      mode: "adaptive",
      minQuestions: 6,
      entropyThreshold: 2.0,
    });

    // Strongly answer investigative items
    let count = 0;
    while (!quiz.isComplete() && count < 48) {
      const q = quiz.nextQuestion();
      if (!q) break;
      // Give 5 to I items, 1 to everything else
      const response = q.type === "I" ? 5 : 1;
      quiz.answer(q.id, response as any);
      count++;
    }

    expect(count).toBeLessThan(48);
    expect(quiz.topTypes(1)[0]).toBe("I");
  });
});

describe("quiz full mode", () => {
  it("asks all 48 questions", () => {
    const quiz = createQuiz({ language: "en", mode: "full" });

    let count = 0;
    while (!quiz.isComplete()) {
      const q = quiz.nextQuestion();
      if (!q) break;
      quiz.answer(q.id, 3);
      count++;
    }

    expect(count).toBe(48);
    expect(quiz.isComplete()).toBe(true);
    expect(quiz.nextQuestion()).toBeNull();
  });
});

describe("topTypes", () => {
  it("returns types sorted by probability", () => {
    const quiz = createQuiz({ language: "en", mode: "full" });

    // Answer with strong I and moderate R
    for (let i = 1; i <= 8; i++) {
      quiz.answer(`I${i}`, 5);
      quiz.answer(`R${i}`, 4);
      quiz.answer(`A${i}`, 1);
      quiz.answer(`S${i}`, 1);
      quiz.answer(`E${i}`, 1);
      quiz.answer(`C${i}`, 1);
    }

    const top = quiz.topTypes(2);
    expect(top[0]).toBe("I");
    expect(top[1]).toBe("R");
  });
});

describe("quiz Spanish language", () => {
  it("loads Spanish items", () => {
    const quiz = createQuiz({ language: "es" });
    const q = quiz.nextQuestion()!;
    // Spanish items should contain Spanish characters
    expect(q.text).toBeTruthy();
    expect(q.id).toMatch(/^[RIASEC]\d$/);
  });
});
