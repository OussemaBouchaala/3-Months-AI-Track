ss = fn("sus_score")
check("SUS: best answers give 100, worst give 0", lambda: ss([5, 1] * 5) == 100 and ss([1, 5] * 5) == 0)
check("SUS: all 3s give 50", lambda: ss([3] * 10) == 50)
check("SUS: odd questions positive, even negative", lambda: ss([4, 2, 5, 1, 4, 2, 5, 2, 4, 1]) == 85.0)
def _bad(a):
    try:
        ss(a)
    except ValueError:
        return True
    return False
check("SUS rejects wrong length or values", lambda: _bad([3] * 9) and _bad([3] * 9 + [6]) and _bad([0] + [3] * 9))
gr = fn("sus_grade")
check("sus_grade thresholds", lambda: [gr(x) for x in (85, 80.3, 75, 68, 67.9, 51, 40)] == ["A", "A", "B", "C", "D", "D", "F"])
tt = fn("task_table")
S = [{"user": "a", "task": "T1", "success": True, "seconds": 30, "errors": 0},
     {"user": "b", "task": "T1", "success": False, "seconds": 200, "errors": 2},
     {"user": "c", "task": "T1", "success": True, "seconds": 50, "errors": 1},
     {"user": "a", "task": "T2", "success": False, "seconds": 90, "errors": 1}]
check("task_table: rate, median of successes only, total errors", lambda: tt(S)["T1"] == {"n": 3, "success_rate": 0.67, "median_seconds": 40, "errors": 3})
check("no success -> median None; tasks in order", lambda: tt(S)["T2"]["median_seconds"] is None and list(tt(S)) == ["T1", "T2"])
md = fn("to_markdown")
check("to_markdown rows", lambda: md(tt(S)).splitlines()[2:] == ["| T1 | 3 | 67% | 40 | 3 |", "| T2 | 1 | 0% | - | 1 |"])
