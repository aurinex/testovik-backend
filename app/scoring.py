from typing import Any

from . import constants


def _pick(answers: list[dict], key: Any, default: Any = None) -> Any:
    for a in answers:
        if a.get("key") == key or a.get("index") == key:
            return a.get("value", default)
    return default


def score_dragdrop(content: dict, answers: list[dict]) -> tuple[int, int, list[dict]]:
    items = content.get("items", [])
    total = len(items)
    correct = 0
    details: list[dict] = []
    for i, item in enumerate(items):
        chosen = _pick(answers, item.get("id") or str(i))
        ok = chosen == item.get("section")
        if ok:
            correct += 1
        details.append(
            {
                "item_id": item.get("id") or str(i),
                "item_text": item.get("text"),
                "expected": item.get("section"),
                "chosen": chosen,
                "correct": ok,
            }
        )
    return correct, total, details


def score_sort(content: dict, answers: list[dict]) -> tuple[int, int, list[dict]]:
    items = content.get("items", [])
    total = len(items)
    correct = 0
    details: list[dict] = []
    for i, item in enumerate(items):
        chosen = _pick(answers, item.get("id") or str(i))
        ok = chosen == item.get("section")
        if ok:
            correct += 1
        details.append(
            {
                "item_id": item.get("id") or str(i),
                "item_text": item.get("text"),
                "expected": item.get("section"),
                "chosen": chosen,
                "correct": ok,
            }
        )
    return correct, total, details


def score_quiz(content: dict, answers: list[dict]) -> tuple[int, int, list[dict]]:
    questions = content.get("questions", [])
    total = len(questions)
    correct = 0
    details: list[dict] = []
    for i, q in enumerate(questions):
        chosen = _pick(answers, q.get("id") or str(i))
        ok = chosen == q.get("correct")
        if ok:
            correct += 1
        details.append(
            {
                "question_id": q.get("id") or str(i),
                "question": q.get("question"),
                "expected": q.get("correct"),
                "chosen": chosen,
                "correct": ok,
            }
        )
    return correct, total, details


def score_true_false(content: dict, answers: list[dict]) -> tuple[int, int, list[dict]]:
    statements = content.get("statements", [])
    total = len(statements)
    correct = 0
    details: list[dict] = []
    for i, s in enumerate(statements):
        chosen = _pick(answers, s.get("id") or str(i))
        ok = chosen == s.get("is_true")
        if ok:
            correct += 1
        details.append(
            {
                "statement_id": s.get("id") or str(i),
                "statement": s.get("statement"),
                "expected": s.get("is_true"),
                "chosen": chosen,
                "correct": ok,
            }
        )
    return correct, total, details


def score_scenario(content: dict, answers: list[dict]) -> tuple[int, int, list[dict]]:
    scenarios = content.get("scenarios", [])
    total = len(scenarios)
    correct = 0
    details: list[dict] = []
    for i, sc in enumerate(scenarios):
        chosen = _pick(answers, sc.get("id") or str(i))
        ok = chosen == sc.get("correct")
        if ok:
            correct += 1
        details.append(
            {
                "scenario_id": sc.get("id") or str(i),
                "title": sc.get("title"),
                "expected": sc.get("correct"),
                "chosen": chosen,
                "correct": ok,
            }
        )
    return correct, total, details


def score_task(task_type: str, content: dict, answers: list[dict]) -> tuple[int, int, list[dict]]:
    answers = [a for a in answers if isinstance(a, dict)]
    if task_type == constants.TASK_DRAGDROP:
        return score_dragdrop(content, answers)
    if task_type == constants.TASK_DRAG3D:
        return score_dragdrop(content, answers)
    if task_type == constants.TASK_SORT:
        return score_sort(content, answers)
    if task_type == constants.TASK_QUIZ:
        return score_quiz(content, answers)
    if task_type == constants.TASK_TRUE_FALSE:
        return score_true_false(content, answers)
    if task_type == constants.TASK_SCENARIO:
        return score_scenario(content, answers)
    return 0, 0, []