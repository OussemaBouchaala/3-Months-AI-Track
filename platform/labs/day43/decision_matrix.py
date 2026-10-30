"""Phase 2 starts: pick ONE project with a weighted decision matrix, not a gut feeling.

1. `CRITERIA` and `OPTIONS`: what matters (with weights) and how each project scores (1-5).
2. `normalize_weights`: weights rescaled to add up to 1.
3. `weighted_score`: one project's total.
4. `rank`: all projects, best first.
5. `sensitivity`: does the winner survive small changes to the weights?

If a tiny change of one weight flips the winner, the choice is fragile: think again
about that criterion. If nothing flips it, the choice is **robust**.
"""

CRITERIA = {                 # weight: how much each criterion matters (any positive numbers)
    "real_user": 3,          # a real person will use it and talk to you
    "data_access": 3,        # you can get the documents within a week
    "arabic": 2,             # uses the Arabic skills from Phase 1
    "action": 2,             # has at least one real action (tool) to perform
    "demo": 1,               # easy to show in a 3-5 minute video
}

OPTIONS = {                  # each option scored 1-5 on each criterion
    "Agency document assistant": {"real_user": 4, "data_access": 4, "arabic": 4, "action": 5, "demo": 4},
    "Contract clause extractor": {"real_user": 3, "data_access": 2, "arabic": 3, "action": 2, "demo": 3},
    "Support chatbot for a shop": {"real_user": 3, "data_access": 3, "arabic": 3, "action": 4, "demo": 5},
}


def normalize_weights(criteria):
    """Scale the weights so they add up to 1, keeping their ratios.

    Weights 3 and 1 become 0.75 and 0.25. After this, a project's score
    stays on the same 1-5 scale as the individual scores, which is easy to
    read. A negative weight, or all weights at 0, makes no sense: refuse it.

    Example:
        >>> normalize_weights({"a": 3, "b": 1})
        {'a': 0.75, 'b': 0.25}
        >>> try:
        ...     normalize_weights({"a": 0, "b": 0})
        ... except ValueError as e:
        ...     print(e)
        all weights are 0
    """
    if any(w < 0 for w in criteria.values()):
        raise ValueError("negative weight")
    total = sum(criteria.values())
    if total == 0:
        raise ValueError("all weights are 0")
    return {k: w / total for k, w in criteria.items()}


def weighted_score(scores, weights):
    """A project's total: the sum of weight x score over the criteria.

    A criterion with no score raises `KeyError` on purpose: a silent 0 would
    quietly punish that project.

    Example:
        >>> weighted_score({"a": 4, "b": 2}, {"a": 0.75, "b": 0.25})
        3.5
    """
    return sum(w * scores[k] for k, w in weights.items())


def rank(options, criteria):
    """All projects as `(name, score)`, best first, scores rounded to 2 decimals.

    The sort key `(-score, name)` sorts by score from high to low, and
    alphabetically when two scores tie, so the order is always the same.

    Example:
        >>> opts = {"B": {"x": 5, "y": 1}, "A": {"x": 1, "y": 5}, "C": {"x": 3, "y": 3}}
        >>> rank(opts, {"x": 3, "y": 1})
        [('B', 4.0), ('C', 3.0), ('A', 2.0)]
        >>> rank(OPTIONS, CRITERIA)[0]
        ('Agency document assistant', 4.18)
    """
    w = normalize_weights(criteria)
    out = [(name, round(weighted_score(s, w), 2)) for name, s in options.items()]
    return sorted(out, key=lambda t: (-t[1], t[0]))


def sensitivity(options, criteria, delta=1):
    """The criteria whose weight, moved by `delta` up or down, changes the winner.

    For each criterion, try its weight +1 and -1 (never below 0) and re-rank.
    `dict(criteria, **{c: new})` copies the weights with one value changed.
    An empty list means the winner is robust.

    Example:
        >>> sensitivity({"P": {"x": 5, "y": 1}, "Q": {"x": 1, "y": 4}}, {"x": 2, "y": 2})
        ['x', 'y']
        >>> sensitivity(OPTIONS, CRITERIA)
        []
    """
    winner = rank(options, criteria)[0][0]
    flips = set()
    for c in criteria:
        for d in (delta, -delta):
            changed = dict(criteria, **{c: max(0, criteria[c] + d)})
            if rank(options, changed)[0][0] != winner:
                flips.add(c)
    return sorted(flips)


if __name__ == "__main__":
    for name, score in rank(OPTIONS, CRITERIA):
        print(f"{score:5.2f}  {name}")
    print("winner changes if you move:", sensitivity(OPTIONS, CRITERIA) or "nothing (robust)")
