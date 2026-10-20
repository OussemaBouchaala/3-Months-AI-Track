cc = fn("check_case")
A = {"question": "q", "expect": "answer", "must_contain": "2 mois"}
I = {"question": "q", "expect": "idk"}
good = {"answer": "La caution est de 2 Mois [1].", "idk": False, "sources": [{"n": 1}], "latency_ms": 900}
idk = {"answer": "I don't know based on the documents.", "idk": True, "sources": [], "latency_ms": 300}
check("a good answer and a good idk pass", lambda: cc(A, 200, good) == [] and cc(I, 200, idk) == [])
check("non-200 -> only the status failure", lambda: cc(A, 503, {}) == ["status 503"])
check("answer case: said idk, no sources, missing text", lambda: set(cc(A, 200, dict(idk, answer="I don't know"))) == {"said idk", "no sources", "missing '2 mois'"})
check("idk case: should be idk, sources on idk", lambda: set(cc(I, 200, good)) == {"should be idk", "sources on idk"})
check("empty answer and slow latency", lambda: set(cc(I, 200, dict(idk, answer=" ", latency_ms=20000), max_latency_ms=15000)) == {"empty answer", "latency 20000 ms"})
rs = fn("run_smoke")
def ask(q):
    if q == "boom":
        raise ConnectionError("refused")
    return (200, good) if q == "ok" else (200, idk)
res = lambda: rs([dict(A, question="ok"), dict(A, question="boom"), dict(I, question="nothing")], ask)
check("run_smoke: one result per case, exceptions become failures", lambda: [r["ok"] for r in res()] == [True, False, True] and res()[1]["failures"] == ["error: ConnectionError"])
sm = fn("summary")
check("summary: count line then FAIL lines", lambda: sm(res()).splitlines() == ["2/3 passed", "FAIL boom: error: ConnectionError"])
ec = fn("exit_code")
check("exit_code 1 on any failure, 0 when all pass", lambda: ec(res()) == 1 and ec([r for r in res() if r["ok"]]) == 0)
check("CASES has at least 6 cases, including 1 idk", lambda: len(var("CASES")) >= 6 and any(c["expect"] == "idk" for c in var("CASES")))
