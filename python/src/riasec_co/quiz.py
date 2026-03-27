"""Bayesian adaptive RIASEC quiz engine."""

from __future__ import annotations

from dataclasses import dataclass, field

from riasec_co.data import Item, load_items
from riasec_co.scoring import DirichletAlpha, expected_info_gain, RIASEC_TYPES


@dataclass
class Answer:
    """A recorded answer."""

    item_id: str
    type: str
    response: int
    keyed: str


@dataclass
class QuizProgress:
    """Quiz progress info."""

    answered: int
    total: int
    estimated_remaining: int
    confidence: float
    entropy: float


class Quiz:
    """Bayesian adaptive RIASEC quiz.

    Parameters
    ----------
    language : str
        Language for item text ("en" or "es"). Default: "es"
    mode : str
        Quiz mode: "adaptive" or "full". Default: "adaptive"
    entropy_threshold : float
        Entropy threshold for adaptive stopping. Default: 1.5
    max_questions : int
        Maximum questions in adaptive mode. Default: 24
    min_questions : int
        Minimum questions in adaptive mode. Default: 12
    """

    def __init__(
        self,
        language: str = "es",
        mode: str = "adaptive",
        entropy_threshold: float = 1.5,
        max_questions: int = 24,
        min_questions: int = 12,
    ):
        self._language = language
        self._mode = mode
        self._entropy_threshold = entropy_threshold
        self._max_questions = max_questions
        self._min_questions = min_questions

        self._items = load_items(language)
        self._alpha = DirichletAlpha()
        self._answered: set[str] = set()
        self._answers: list[Answer] = []

    def next_question(self) -> Item | None:
        """Get the next question. Returns None if quiz is complete."""
        if self.is_complete:
            return None

        remaining = [i for i in self._items if i.id not in self._answered]
        if not remaining:
            return None

        if self._mode == "full":
            return remaining[0]

        # Adaptive: pick item with highest expected information gain
        best_item = remaining[0]
        best_gain = -float("inf")
        for item in remaining:
            gain = expected_info_gain(self._alpha, item.type)
            if gain > best_gain:
                best_gain = gain
                best_item = item
        return best_item

    def answer(self, item_id: str, response: int) -> None:
        """Record an answer (response: 1-5 Likert scale)."""
        item = next((i for i in self._items if i.id == item_id), None)
        if item is None:
            raise ValueError(f"Unknown item: {item_id}")
        if item_id in self._answered:
            raise ValueError(f"Item already answered: {item_id}")
        if not 1 <= response <= 5:
            raise ValueError(f"Invalid response: {response}")

        self._answered.add(item_id)
        self._alpha = self._alpha.update(item.type, response, item.keyed)
        self._answers.append(
            Answer(item_id=item_id, type=item.type, response=response, keyed=item.keyed)
        )

    @property
    def is_complete(self) -> bool:
        """Check if the quiz should stop."""
        n = len(self._answered)
        if self._mode == "full":
            return n >= len(self._items)
        if n >= self._max_questions:
            return True
        if n < self._min_questions:
            return False
        return self._alpha.entropy < self._entropy_threshold

    @property
    def profile(self) -> dict[str, float]:
        """Current RIASEC profile (posterior mean)."""
        return self._alpha.posterior_mean()

    @property
    def alpha(self) -> DirichletAlpha:
        """Current Dirichlet alpha parameters."""
        return self._alpha

    @property
    def answers(self) -> list[Answer]:
        """All recorded answers."""
        return list(self._answers)

    def progress(self) -> QuizProgress:
        """Get current progress."""
        n = len(self._answered)
        total = len(self._items) if self._mode == "full" else self._max_questions
        ent = self._alpha.entropy
        conf = self._alpha.confidence

        if self._mode == "full":
            remaining = len(self._items) - n
        elif n < self._min_questions:
            remaining = self._min_questions - n
        elif ent < self._entropy_threshold:
            remaining = 0
        else:
            remaining = min(
                self._max_questions - n,
                int((ent - self._entropy_threshold) * 8) + 1,
            )

        return QuizProgress(
            answered=n,
            total=total,
            estimated_remaining=remaining,
            confidence=conf,
            entropy=ent,
        )

    def top_types(self, n: int = 3) -> list[str]:
        """Get the top N RIASEC types by probability."""
        profile = self.profile
        return [t for t, _ in sorted(profile.items(), key=lambda x: -x[1])[:n]]
