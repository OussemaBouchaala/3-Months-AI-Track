import io, json, logging
rd = fn("redact")
check("redact masks email, phone, CIN", lambda: rd("a.b@x.tn, +216 98 123 456, CIN 01234567, 2025") == "[EMAIL], [PHONE], CIN [CIN], 2025")
Fmt = var("JsonFormatter")
def _log(**extra):
    buf = io.StringIO()
    lg = logging.getLogger(f"bench_check_{len(extra)}_{id(buf)}")
    lg.handlers.clear(); lg.propagate = False; lg.setLevel(logging.INFO)
    h = logging.StreamHandler(buf); h.setFormatter(Fmt()); lg.addHandler(h)
    lg.info("asked by 22333444", extra=extra)
    return json.loads(buf.getvalue().strip().splitlines()[-1])
check("JsonFormatter: one JSON object with ts, level, logger, msg", lambda: (lambda d: d["level"] == "INFO" and d["msg"] == "asked by [PHONE]" and d["ts"].endswith("+00:00") and "logger" in d)(_log()))
check("JsonFormatter adds known extras and redacts the question", lambda: (lambda d: d["request_id"] == "r1" and d["question"] == "call [PHONE] ؟" and d["stage_ms"] == {"retrieve": 12} and "password" not in d)(_log(request_id="r1", question="call 98123456 ؟", stage_ms={"retrieve": 12}, password="x")))
tm = fn("timed")
t = iter([10.0, 10.25, 20.0, 20.5])
def _timed():
    st = {}
    with tm(st, "retrieve", clock=lambda: next(t)):
        pass
    try:
        with tm(st, "generate", clock=lambda: next(t)):
            raise TimeoutError
    except TimeoutError:
        pass
    return st == {"retrieve": 250, "generate": 500}
check("timed records milliseconds, even when the block raises", _timed)
M = var("Metrics")
def _snap():
    m = M()
    for v in range(1, 21):
        m.observe("total_ms", v * 100)
    m.inc("requests", 20); m.inc("status_ok")
    return m.snapshot()
check("Metrics.snapshot: counters and p50/p95/max", lambda: _snap() == {"counters": {"requests": 20, "status_ok": 1}, "histograms": {"total_ms": {"count": 20, "p50": 1000, "p95": 1900, "max": 2000}}})
lr = fn("log_request")
def _lr():
    buf = io.StringIO()
    lg = logging.getLogger("bench_check_lr"); lg.handlers.clear(); lg.propagate = False; lg.setLevel(logging.INFO)
    h = logging.StreamHandler(buf); h.setFormatter(Fmt()); lg.addHandler(h)
    m = M()
    lr(lg, m, "abc", "caution ? 98123456", {"retrieve": 40, "generate": 900}, "ok")
    d = json.loads(buf.getvalue())
    s = m.snapshot()
    return (d["total_ms"] == 940 and d["status"] == "ok" and "[PHONE]" in d["question"] and s["counters"] == {"requests": 1, "status_ok": 1}
            and s["histograms"]["generate_ms"]["max"] == 900 and s["histograms"]["total_ms"]["count"] == 1)
check("log_request: one line with total, and metrics updated", _lr)
