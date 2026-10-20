# A smoke test: 8 questions through the running service, in 30 seconds, before anyone else touches it.
# Not an evaluation (that's Week 10): just "is the whole path alive and sane?". Exit code 1 if not.

CASES = [   # edit with your own documents' facts
    {"question": "Combien de mois de caution pour une location à l'année ?", "expect": "answer", "must_contain": "2"},
    {"question": "شنية الوثائق اللازمة باش نكري؟", "expect": "answer"},
    {"question": "Can I visit on Sunday?", "expect": "answer"},
    {"question": "Do you sell cars?", "expect": "idk"},
]
MAX_LATENCY_MS = 15000


def check_case(case, status, body, max_latency_ms=MAX_LATENCY_MS):
    """List of failure strings for one response ([] = pass):
    "status 500" if status != 200 (and nothing else is checked);
    "empty answer"; "latency 16000 ms"  (> max_latency_ms);
    expect "answer": "said idk" if body["idk"], "no sources" if no sources,
                     "missing '2'" if must_contain (case-insensitive) is not in the answer;
    expect "idk": "should be idk" if not body["idk"], "sources on idk" if it has sources."""
    # TODO
    ...


def run_smoke(cases, ask):
    """ask(question) -> (status, body). Return [{"question", "ok", "failures"}]. An exception from ask is a
    failure "error: <ExceptionName>", not a crash."""
    # TODO
    ...


def summary(results):
    """First line "3/4 passed", then one line per failed case: "FAIL <question>: <failures joined by ', '>"."""
    # TODO
    ...


def exit_code(results):
    """0 when every case passed, else 1 (so a script or CI can stop)."""
    # TODO
    ...


if __name__ == "__main__":
    import sys
    import httpx
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"

    def ask(q):
        r = httpx.post(f"{url}/ask", json={"question": q}, timeout=60)
        return r.status_code, (r.json() if r.headers.get("content-type", "").startswith("application/json") else {})

    res = run_smoke(CASES, ask)
    print(summary(res))
    sys.exit(exit_code(res))
