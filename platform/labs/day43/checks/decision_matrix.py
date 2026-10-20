nw = fn("normalize_weights")
check("normalize_weights sums to 1 and keeps the ratios", lambda: approx(sum(nw({"a": 3, "b": 1}).values()), 1) and approx(nw({"a": 3, "b": 1})["a"], 0.75))
def _raises(f, *a):
    try:
        f(*a)
    except ValueError:
        return True
    return False
check("negative or all-zero weights raise ValueError", lambda: _raises(nw, {"a": -1, "b": 2}) and _raises(nw, {"a": 0, "b": 0}))
ws = fn("weighted_score")
check("weighted_score is the weighted sum", lambda: approx(ws({"a": 4, "b": 2}, {"a": 0.75, "b": 0.25}), 3.5))
def _keyerr():
    try:
        ws({"a": 4}, {"a": 0.5, "b": 0.5})
    except KeyError:
        return True
    return False
check("a missing score raises KeyError (no silent zero)", _keyerr)
rk = fn("rank")
opts = {"B": {"x": 5, "y": 1}, "A": {"x": 1, "y": 5}, "C": {"x": 3, "y": 3}}
check("rank sorts best first, rounded scores", lambda: rk(opts, {"x": 3, "y": 1}) == [("B", 4.0), ("C", 3.0), ("A", 2.0)])
check("ties are broken alphabetically", lambda: [n for n, _ in rk(opts, {"x": 1, "y": 1})] == ["A", "B", "C"])
sv = fn("sensitivity")
check("sensitivity finds the criteria that flip the winner", lambda: sv({"P": {"x": 5, "y": 1}, "Q": {"x": 1, "y": 4}}, {"x": 2, "y": 2}) == ["x", "y"])
check("sensitivity is [] for a robust winner", lambda: sv({"P": {"x": 5, "y": 5}, "Q": {"x": 1, "y": 1}}, {"x": 2, "y": 1}) == [])
check("your OPTIONS score every criterion 1-5", lambda: all(set(s) == set(var("CRITERIA")) and all(1 <= v <= 5 for v in s.values()) for s in var("OPTIONS").values()) and len(var("OPTIONS")) >= 2)
