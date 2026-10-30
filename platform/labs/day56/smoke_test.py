"""A smoke test: 7 questions through the running service, in 30 seconds, before anyone else touches it.

Not an evaluation (that's Week 10): just "is the whole path alive and sane?". It exits
with code 1 if not, so a script or CI can stop there.

1. `CASES`: questions with what you expect (an answer, or "I don't know").
2. `check_case`: everything wrong with one response.
3. `run_smoke`: all cases through an `ask` function; errors don't crash the run.
4. `summary` and `exit_code`: the readable result and the signal for scripts.
"""

CASES = [   # edit with your own documents' facts
    {"question": "Combien de mois de caution pour une location à l'année ?", "expect": "answer", "must_contain": "2"},
    {"question": "شنية الوثائق اللازمة باش نكري؟", "expect": "answer"},
    {"question": "Can I visit on Sunday?", "expect": "answer"},
    {"question": "Le loyer peut augmenter de combien après un an ?", "expect": "answer", "must_contain": "5"},
    {"question": "Est-ce que les animaux sont acceptés ?", "expect": "answer"},
    {"question": "Do you sell cars?", "expect": "idk"},
    {"question": "شكون رئيس البلدية؟", "expect": "idk"},
]
MAX_LATENCY_MS = 15000


def check_case(case, status, body, max_latency_ms=MAX_LATENCY_MS):
    """All the failures of one response, as short strings (`[]` = pass).

    - Not HTTP 200: `"status 503"`, and nothing else is checked (there's no
      body worth reading).
    - Always: the answer isn't empty, the latency is under the limit.
    - `expect: "answer"`: not IDK, has sources, contains `must_contain`
      (ignoring case) when the case gives one.
    - `expect: "idk"`: is IDK, and has no sources (citing something while
      saying "I don't know" is a bug).

    Example:
        >>> case = {"question": "q", "expect": "answer", "must_contain": "2 mois"}
        >>> good = {"answer": "La caution est de 2 Mois [1].", "idk": False, "sources": [{"n": 1}], "latency_ms": 900}
        >>> check_case(case, 200, good)
        []
        >>> check_case(case, 503, {})
        ['status 503']
        >>> check_case({"question": "q", "expect": "idk"}, 200, dict(good, latency_ms=20000))
        ['latency 20000 ms', 'should be idk', 'sources on idk']
    """
    if status != 200:
        return [f"status {status}"]
    fails = []
    if not body.get("answer", "").strip():
        fails.append("empty answer")
    if body.get("latency_ms", 0) > max_latency_ms:
        fails.append(f"latency {body['latency_ms']} ms")
    if case["expect"] == "answer":
        if body.get("idk"):
            fails.append("said idk")
        if not body.get("sources"):
            fails.append("no sources")
        if case.get("must_contain") and case["must_contain"].lower() not in body.get("answer", "").lower():
            fails.append(f"missing '{case['must_contain']}'")
    else:
        if not body.get("idk"):
            fails.append("should be idk")
        if body.get("sources"):
            fails.append("sources on idk")
    return fails


def run_smoke(cases, ask):
    """Run every case through `ask(question) -> (status, body)`.

    An exception (server down, timeout) becomes the failure
    `"error: ConnectionError"` for that case, and the run continues: you
    want the full picture, not the first crash.

    Example:
        >>> def ask(q):
        ...     if q == "boom":
        ...         raise ConnectionError("refused")
        ...     return 200, {"answer": "I don't know", "idk": True, "sources": [], "latency_ms": 5}
        >>> run_smoke([{"question": "boom", "expect": "idk"}, {"question": "cars?", "expect": "idk"}], ask)
        [{'question': 'boom', 'ok': False, 'failures': ['error: ConnectionError']}, {'question': 'cars?', 'ok': True, 'failures': []}]
    """
    results = []
    for case in cases:
        try:
            status, body = ask(case["question"])
            fails = check_case(case, status, body)
        except Exception as e:
            fails = [f"error: {type(e).__name__}"]
        results.append({"question": case["question"], "ok": not fails, "failures": fails})
    return results


def summary(results):
    """`"2/3 passed"`, then one `FAIL question: failures` line per failed case.

    Example:
        >>> print(summary([{"question": "a", "ok": True, "failures": []},
        ...                {"question": "boom", "ok": False, "failures": ["error: ConnectionError", "no sources"]}]))
        1/2 passed
        FAIL boom: error: ConnectionError, no sources
    """
    lines = [f"{sum(r['ok'] for r in results)}/{len(results)} passed"]
    lines += [f"FAIL {r['question']}: {', '.join(r['failures'])}" for r in results if not r["ok"]]
    return "\n".join(lines)


def exit_code(results):
    """0 when every case passed, else 1. Shells and CI read this number:
    `python smoke_test.py && deploy` only deploys on 0.

    Example:
        >>> exit_code([{"ok": True}]), exit_code([{"ok": True}, {"ok": False}])
        (0, 1)
    """
    return 0 if all(r["ok"] for r in results) else 1


def run_against(url="http://127.0.0.1:8000"):
    """The real smoke test against your running day 55 service.

    Example (note): needs `python ../day55/pipeline_service.py --serve` running.
        >>> run_against()  # doctest: +SKIP
    """
    import httpx

    def ask(q):
        r = httpx.post(f"{url}/ask", json={"question": q}, timeout=60)
        return r.status_code, (r.json() if r.headers.get("content-type", "").startswith("application/json") else {})

    res = run_smoke(CASES, ask)
    print(summary(res))
    return exit_code(res)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        sys.exit(run_against(sys.argv[1]))
    # Demo: a fake service that is right most of the time, slow once, and ignores Derja.
    IDK = "I don't know based on the documents."

    def fake_ask(q):
        if "visit" in q:
            return 200, {"answer": "Yes, Sunday 10-13h [1].", "idk": False, "sources": [{"n": 1}], "latency_ms": 16500}
        if "cars" in q or "البلدية" in q or "الوثائق" in q:
            return 200, {"answer": IDK, "idk": True, "sources": [], "latency_ms": 400}
        if "loyer" in q:
            return 200, {"answer": "Une hausse de 5% par an maximum [2].", "idk": False, "sources": [{"n": 2}], "latency_ms": 2100}
        return 200, {"answer": "Deux mois (2) de caution [1].", "idk": False, "sources": [{"n": 1}], "latency_ms": 1800}

    res = run_smoke(CASES, fake_ask)
    print(summary(res))
    print("exit code would be", exit_code(res))
