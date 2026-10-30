"""Watch 3-5 real users try the page with real tasks, and measure it.

Did they finish? How long did it take? How usable did it feel? The last one uses the
**System Usability Scale** (SUS): 10 standard questions, a score from 0 to 100. Numbers,
not "they seemed to like it".

1. `SUS_QUESTIONS`: the 10 questions, in their fixed order.
2. `sus_score` and `sus_grade`: one user's answers -> a score -> a letter.
3. `task_table`: success rate, median time and errors per task.
4. `to_markdown`: that table, ready for the usability report (day 63).
"""
import statistics

SUS_QUESTIONS = [            # answered 1 (strongly disagree) to 5 (strongly agree)
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
    """One user's SUS score, 0-100.

    The questions alternate: the 1st, 3rd, 5th... are positive ("easy to
    use"), so agreeing is good: they add `answer - 1`. The 2nd, 4th... are
    negative ("cumbersome"), so disagreeing is good: they add `5 - answer`.
    Each question gives 0-4 points, 10 questions give 0-40, times 2.5 -> 0-100.

    `enumerate` counts from 0, so `i % 2 == 0` means the 1st, 3rd... question.

    Example:
        >>> sus_score([5, 1] * 5), sus_score([1, 5] * 5), sus_score([3] * 10)
        (100.0, 0.0, 50.0)
        >>> sus_score([4, 2, 5, 1, 4, 2, 5, 2, 4, 1])
        85.0
    """
    if len(answers) != 10 or any(a not in (1, 2, 3, 4, 5) for a in answers):
        raise ValueError("SUS needs 10 answers between 1 and 5")
    return sum((a - 1) if i % 2 == 0 else (5 - a) for i, a in enumerate(answers)) * 2.5


def sus_grade(score):
    """A letter from published SUS benchmarks: 68 is the average product.

    A from 80.3, B from 74, C from 68, D from 51, else F. The loop returns
    the first grade whose limit the score reaches.

    Example:
        >>> [sus_grade(x) for x in (85, 75, 68, 67.9, 40)]
        ['A', 'B', 'C', 'D', 'F']
    """
    for limit, grade in ((80.3, "A"), (74, "B"), (68, "C"), (51, "D")):
        if score >= limit:
            return grade
    return "F"


def task_table(sessions):
    """Per task: attempts, success rate, median time, total errors.

    - Group sessions by task (`setdefault` creates the list the first time;
      dicts keep insertion order, so tasks stay in the order you ran them).
    - The **median** time counts **successful** attempts only: someone who
      gave up after 3 minutes didn't take 3 minutes to succeed.
    - The median, not the mean: one slow user doesn't distort it.

    Example:
        >>> S = [{"task": "T1", "success": True, "seconds": 30, "errors": 0},
        ...      {"task": "T1", "success": False, "seconds": 200, "errors": 2},
        ...      {"task": "T1", "success": True, "seconds": 50, "errors": 1},
        ...      {"task": "T2", "success": False, "seconds": 90, "errors": 1}]
        >>> task_table(S)
        {'T1': {'n': 3, 'success_rate': 0.67, 'median_seconds': 40.0, 'errors': 3}, 'T2': {'n': 1, 'success_rate': 0.0, 'median_seconds': None, 'errors': 1}}
    """
    out = {}
    for s in sessions:
        out.setdefault(s["task"], []).append(s)
    table = {}
    for task, rows in out.items():
        ok = [r["seconds"] for r in rows if r["success"]]
        table[task] = {"n": len(rows), "success_rate": round(sum(r["success"] for r in rows) / len(rows), 2),
                       "median_seconds": statistics.median(ok) if ok else None, "errors": sum(r["errors"] for r in rows)}
    return table


def to_markdown(table):
    """The table as Markdown for the report. `{:.0%}` shows 0.67 as "67%";
    a task nobody finished shows "-" for its time.

    Example:
        >>> print(to_markdown({"T1": {"n": 3, "success_rate": 0.67, "median_seconds": 40, "errors": 3},
        ...                    "T2": {"n": 1, "success_rate": 0.0, "median_seconds": None, "errors": 1}}))
        | task | n | success | median s | errors |
        |---|---|---|---|---|
        | T1 | 3 | 67% | 40 | 3 |
        | T2 | 1 | 0% | - | 1 |
    """
    lines = ["| task | n | success | median s | errors |", "|---|---|---|---|---|"]
    for task, r in table.items():
        med = "-" if r["median_seconds"] is None else f"{r['median_seconds']:.0f}"
        lines.append(f"| {task} | {r['n']} | {r['success_rate']:.0%} | {med} | {r['errors']} |")
    return "\n".join(lines)


if __name__ == "__main__":
    # Three agents tested the page; replace with what your users answered and did.
    sus = {"Salma": [4, 2, 5, 1, 4, 2, 5, 2, 4, 1], "Karim": [3, 3, 4, 2, 3, 2, 4, 3, 3, 2], "Ines": [5, 1, 5, 1, 4, 1, 5, 1, 5, 2]}
    scores = {u: sus_score(a) for u, a in sus.items()}
    mean = sum(scores.values()) / len(scores)
    print("SUS:", scores, f"mean {mean:.1f} -> grade {sus_grade(mean)}")
    sessions = [
        {"user": "Salma", "task": "deposit question", "success": True, "seconds": 35, "errors": 0},
        {"user": "Karim", "task": "deposit question", "success": True, "seconds": 52, "errors": 1},
        {"user": "Ines", "task": "deposit question", "success": True, "seconds": 28, "errors": 0},
        {"user": "Salma", "task": "book a visit", "success": True, "seconds": 95, "errors": 1},
        {"user": "Karim", "task": "book a visit", "success": False, "seconds": 180, "errors": 3},
        {"user": "Ines", "task": "book a visit", "success": True, "seconds": 70, "errors": 0},
    ]
    print(to_markdown(task_table(sessions)))
