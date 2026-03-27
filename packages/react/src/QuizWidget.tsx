import { useState, useCallback, useMemo } from "react";
import {
  createQuiz,
  type Quiz,
  type Item,
  type QuizConfig,
  type RIASECProfile,
  type LikertResponse,
} from "riasec-co";

/** Likert scale labels by language */
const LIKERT_LABELS = {
  en: ["Very inaccurate", "Inaccurate", "Neutral", "Accurate", "Very accurate"],
  es: ["Muy impreciso", "Impreciso", "Neutral", "Preciso", "Muy preciso"],
} as const;

export interface QuizWidgetProps {
  /** Quiz configuration */
  config?: Partial<QuizConfig>;
  /** Called when quiz completes with the final RIASEC profile */
  onComplete?: (profile: RIASECProfile) => void;
  /** Called after each answer with current profile */
  onAnswer?: (profile: RIASECProfile) => void;
  /** Additional CSS class name */
  className?: string;
}

/**
 * Interactive RIASEC quiz widget.
 *
 * Renders one question at a time with Likert scale buttons.
 * Tracks progress and calls onComplete when done.
 */
export function QuizWidget({
  config,
  onComplete,
  onAnswer,
  className,
}: QuizWidgetProps) {
  const language: "en" | "es" = config?.language ?? "es";
  const labels = LIKERT_LABELS[language];

  const quiz = useMemo(() => createQuiz(config), []);
  const [question, setQuestion] = useState<Item | null>(quiz.nextQuestion());
  const [progress, setProgress] = useState(quiz.progress());
  const [completed, setCompleted] = useState(false);

  const handleAnswer = useCallback(
    (response: LikertResponse) => {
      if (!question) return;

      quiz.answer(question.id, response);
      const profile = quiz.profile();
      onAnswer?.(profile);

      if (quiz.isComplete()) {
        setCompleted(true);
        setQuestion(null);
        onComplete?.(profile);
      } else {
        setQuestion(quiz.nextQuestion());
      }
      setProgress(quiz.progress());
    },
    [question, quiz, onComplete, onAnswer]
  );

  if (completed) {
    return (
      <div className={className} data-testid="quiz-complete">
        <p>
          {language === "es"
            ? "¡Cuestionario completado!"
            : "Quiz completed!"}
        </p>
      </div>
    );
  }

  if (!question) return null;

  const pct = Math.round(
    (progress.answered / progress.total) * 100
  );

  return (
    <div className={className} data-testid="quiz-widget">
      {/* Progress bar */}
      <div role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
        <div style={{ width: `${pct}%` }} />
        <span>
          {progress.answered}/{progress.total}
        </span>
      </div>

      {/* Question */}
      <p data-testid="quiz-question">{question.text}</p>

      {/* Likert buttons */}
      <div role="group" aria-label={language === "es" ? "Escala de respuesta" : "Response scale"}>
        {([1, 2, 3, 4, 5] as LikertResponse[]).map((value) => (
          <button
            key={value}
            onClick={() => handleAnswer(value)}
            data-testid={`likert-${value}`}
            aria-label={labels[value - 1]}
          >
            <span>{value}</span>
            <span>{labels[value - 1]}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
