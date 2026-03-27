"""Tests for the Quiz engine."""

import pytest

from riasec_co.quiz import Quiz
from riasec_co.scoring import RIASEC_TYPES


def test_quiz_creates_with_defaults():
    quiz = Quiz(language="en")
    assert not quiz.is_complete
    assert quiz.answers == []


def test_quiz_returns_first_question():
    quiz = Quiz(language="en")
    q = quiz.next_question()
    assert q is not None
    assert q.id
    assert q.text
    assert q.type in RIASEC_TYPES


def test_quiz_records_answer():
    quiz = Quiz(language="en")
    q = quiz.next_question()
    quiz.answer(q.id, 5)
    assert len(quiz.answers) == 1
    assert quiz.answers[0].item_id == q.id
    assert quiz.answers[0].response == 5
    assert quiz.profile[q.type] > 1 / 6


def test_quiz_rejects_duplicate_answer():
    quiz = Quiz(language="en")
    q = quiz.next_question()
    quiz.answer(q.id, 3)
    with pytest.raises(ValueError, match="already answered"):
        quiz.answer(q.id, 4)


def test_quiz_rejects_invalid_response():
    quiz = Quiz(language="en")
    q = quiz.next_question()
    with pytest.raises(ValueError, match="Invalid response"):
        quiz.answer(q.id, 0)
    with pytest.raises(ValueError, match="Invalid response"):
        quiz.answer(q.id, 6)


def test_quiz_rejects_unknown_item():
    quiz = Quiz(language="en")
    with pytest.raises(ValueError, match="Unknown item"):
        quiz.answer("NONEXISTENT", 3)


def test_quiz_progress():
    quiz = Quiz(language="en")
    p0 = quiz.progress()
    assert p0.answered == 0
    assert abs(p0.confidence) < 0.01
    assert p0.entropy > 2

    q = quiz.next_question()
    quiz.answer(q.id, 5)
    p1 = quiz.progress()
    assert p1.answered == 1
    assert p1.confidence > 0


def test_quiz_adaptive_stops_early():
    quiz = Quiz(
        language="en",
        mode="adaptive",
        min_questions=6,
        entropy_threshold=2.0,
    )
    count = 0
    while not quiz.is_complete and count < 48:
        q = quiz.next_question()
        if q is None:
            break
        response = 5 if q.type == "I" else 1
        quiz.answer(q.id, response)
        count += 1

    assert count < 48
    assert quiz.top_types(1)[0] == "I"


def test_quiz_full_mode():
    quiz = Quiz(language="en", mode="full")
    count = 0
    while not quiz.is_complete:
        q = quiz.next_question()
        if q is None:
            break
        quiz.answer(q.id, 3)
        count += 1

    assert count == 48
    assert quiz.is_complete
    assert quiz.next_question() is None


def test_quiz_top_types():
    quiz = Quiz(language="en", mode="full")
    for i in range(1, 9):
        quiz.answer(f"I{i}", 5)
        quiz.answer(f"R{i}", 4)
        quiz.answer(f"A{i}", 1)
        quiz.answer(f"S{i}", 1)
        quiz.answer(f"E{i}", 1)
        quiz.answer(f"C{i}", 1)

    top = quiz.top_types(2)
    assert top[0] == "I"
    assert top[1] == "R"


def test_quiz_spanish():
    quiz = Quiz(language="es")
    q = quiz.next_question()
    assert q is not None
    assert q.text
