# Watch 3-5 real users try the page with real tasks. Measure: did they finish, how long, and how usable it felt
# (the 10-question System Usability Scale). Numbers, not "they seemed to like it".
import statistics

SUS_QUESTIONS = [
    "I think that I would like to use this system frequently.",
    "I found the system unnecessarily complex.",
    "I thought the system was easy to use.",
    "I think that I would need the support of a technical person to be able to use this system.",
    "I found the various functions in this system were well integrated.",
    "I thought there was too much inconsistency in this system.",
    "I would imagine that most people would learn to use this system very quickly.",
    "I found the system very cumbersome to use.",
    "I felt very confident using the system.",
    "I needed to learn a lot of things before I could get going with this system.",
]


def sus_score(answers):
    """answers: 10 integers 1-5 (1 = strongly disagree), in question order. Odd questions (1st, 3rd...) are positive:
    contribute answer - 1. Even ones are negative: 5 - answer. Sum x 2.5 -> 0-100.
    ValueError if not exactly 10 answers or any outside 1-5."""
    # TODO
    ...


def sus_grade(score):
    """A >= 80.3, B >= 74, C >= 68 (the average), D >= 51, else F."""
    # TODO
    ...


def task_table(sessions):
    """sessions: [{"user": "u1", "task": "deposit question", "success": bool, "seconds": float, "errors": int}, ...]
    -> {task: {"n", "success_rate" (rounded 2), "median_seconds" (successful attempts only, None if none), "errors"
    (total)}}, tasks in first-appearance order."""
    # TODO
    ...


def to_markdown(table):
    """| task | n | success | median s | errors |, success as a percentage without decimals ("67%"), median with
    no decimals or "-" when None."""
    # TODO
    ...


if __name__ == "__main__":
    sus = {"Salma": [4, 2, 5, 1, 4, 2, 5, 2, 4, 1], "Karim": [3, 3, 4, 2, 3, 2, 4, 3, 3, 2], "Ines": [5, 1, 5, 1, 4, 1, 5, 1, 5, 2]}
    scores = {u: sus_score(a) for u, a in sus.items()}
    mean = sum(scores.values()) / len(scores)
    print(scores, f"mean {mean:.1f} -> grade {sus_grade(mean)}")
    sessions = [
        {"user": "Salma", "task": "deposit question", "success": True, "seconds": 35, "errors": 0},
        {"user": "Karim", "task": "deposit question", "success": True, "seconds": 52, "errors": 1},
        {"user": "Ines", "task": "deposit question", "success": True, "seconds": 28, "errors": 0},
        {"user": "Salma", "task": "book a visit", "success": True, "seconds": 95, "errors": 1},
        {"user": "Karim", "task": "book a visit", "success": False, "seconds": 180, "errors": 3},
        {"user": "Ines", "task": "book a visit", "success": True, "seconds": 70, "errors": 0},
    ]
    print(to_markdown(task_table(sessions)))
