"""When the agent says "it was slow at 10:42" or "it gave a wrong answer this morning", you
need to find **that** request.

So: one JSON log line per request, with its id, the time of each stage and its status,
and no personal data. Plus counters and latency percentiles at `GET /metrics`.

1. `redact`: emails, phones and CINs out of anything logged.
2. `JsonFormatter`: each log record becomes one JSON line.
3. `timed`: measure a stage with a `with` block.
4. `Metrics`: counters and p50/p95/max per measurement.
5. `log_request`: the one line per request, and the metrics update.
6. `setup_logging`: a logger that writes JSON lines.
"""
import json
import logging
import math
import re
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone

EXTRA_FIELDS = ("request_id", "stage_ms", "status", "question", "n_chunks", "model", "total_ms")
PII = [(re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"), "[EMAIL]"),
       (re.compile(r"(?<!\d)(?:(?:\+|00)216[ .]?)?[2-9]\d(?:[ .]?\d{3}){2}(?!\d)"), "[PHONE]"),
       (re.compile(r"(?<!\d)[01]\d{7}(?!\d)"), "[CIN]")]


def redact(text):
    """Apply every PII pattern, in order (day 45's patterns, simplified).

    Logs are copied, shipped and kept for months: personal data in them
    leaks the longest.

    Example:
        >>> redact("a.b@x.tn, +216 98 123 456, CIN 01234567, 2025")
        '[EMAIL], [PHONE], CIN [CIN], 2025'
    """
    for pat, repl in PII:
        text = pat.sub(repl, text)
    return text


class JsonFormatter(logging.Formatter):
    """Turns each log record into one JSON line.

    Python's `logging` calls a formatter's `format(record)` to turn a record
    into text. JSON lines can be searched and filtered by any log tool
    (`grep '"status": "error"'`, or `jq`).

    Example:
        >>> isinstance(JsonFormatter(), logging.Formatter)
        True
    """

    def format(self, record):
        """Build the JSON for one record.

        - Always: `ts` (UTC time, from `record.created`), `level`, `logger`,
          and the message, redacted.
        - Plus every field of `EXTRA_FIELDS` the call passed with
          `extra={...}`; the question is redacted. Anything else (a password
          someone passed by mistake) is **not** logged: an allow-list.

        Example:
            >>> r = logging.LogRecord("assistant", logging.INFO, "", 0, "asked by 22333444", None, None)
            >>> r.created, r.request_id, r.password = 1798794000, "r1", "hunter2"
            >>> print(JsonFormatter().format(r))
            {"ts": "2027-01-01T09:00:00+00:00", "level": "INFO", "logger": "assistant", "msg": "asked by [PHONE]", "request_id": "r1"}
        """
        data = {"ts": datetime.fromtimestamp(record.created, timezone.utc).isoformat(timespec="seconds"),
                "level": record.levelname, "logger": record.name, "msg": redact(record.getMessage())}
        for f in EXTRA_FIELDS:
            if hasattr(record, f):
                v = getattr(record, f)
                data[f] = redact(v) if f == "question" and isinstance(v, str) else v
        return json.dumps(data, ensure_ascii=False)


@contextmanager
def timed(stages, name, clock=time.perf_counter):
    """`with timed(stages, "retrieve"): ...` stores the block's duration in
    milliseconds in `stages["retrieve"]`.

    `@contextmanager` turns this generator into a `with` block: the code
    before `yield` runs on entry, the `finally` on exit. Because it's a
    `finally`, a stage that crashes (a timeout) still gets its time
    recorded, which is exactly the slow request you want to see.

    Example (a fake clock that returns 10.0 then 10.25 seconds):
        >>> stages, ticks = {}, iter([10.0, 10.25])
        >>> with timed(stages, "retrieve", clock=lambda: next(ticks)):
        ...     pass
        >>> stages
        {'retrieve': 250}
    """
    t0 = clock()
    try:
        yield
    finally:
        stages[name] = int((clock() - t0) * 1000)


class Metrics:
    """Counters and measurements kept in memory, shown at `GET /metrics`.

    `inc` adds to a counter (requests, errors); `observe` stores a value
    (a latency). Enough for one server; Prometheus does the same at scale.

    Example:
        >>> m = Metrics()
        >>> m.inc("requests"); m.inc("requests"); m.observe("total_ms", 900)
        >>> m.counters, m.values
        ({'requests': 2}, {'total_ms': [900]})
    """

    def __init__(self):
        self.counters, self.values = {}, {}

    def inc(self, name, n=1):
        self.counters[name] = self.counters.get(name, 0) + n

    def observe(self, name, value):
        self.values.setdefault(name, []).append(value)

    def snapshot(self):
        """Everything as one dict: the counters, and for each measurement
        its count, p50, p95 (nearest rank) and max.

        The p95 is what the slowest users feel; the max shows the outliers.

        Example:
            >>> m = Metrics()
            >>> for v in range(1, 21):
            ...     m.observe("total_ms", v * 100)
            >>> m.snapshot()
            {'counters': {}, 'histograms': {'total_ms': {'count': 20, 'p50': 1000, 'p95': 1900, 'max': 2000}}}
        """
        def pct(s, p):
            return s[max(1, math.ceil(p / 100 * len(s))) - 1]
        hist = {}
        for name, vals in self.values.items():
            s = sorted(vals)
            hist[name] = {"count": len(s), "p50": pct(s, 50), "p95": pct(s, 95), "max": s[-1]}
        return {"counters": dict(self.counters), "histograms": hist}


def log_request(logger, metrics, request_id, question, stages, status):
    """At the end of each request: one log line, and the metrics updated.

    The line carries the request id (from day 55's middleware), the
    redacted question, every stage's time, the total and the status. The
    metrics count requests per status and record each stage's time.

    Example:
        >>> m = Metrics()
        >>> log_request(logging.getLogger("silent"), m, "abc", "caution ?", {"retrieve": 40, "generate": 900}, "ok")
        >>> m.snapshot()["counters"], m.snapshot()["histograms"]["total_ms"]["max"]
        ({'requests': 1, 'status_ok': 1}, 940)
    """
    total = sum(stages.values())
    logger.info("request", extra={"request_id": request_id, "question": question, "stage_ms": dict(stages), "status": status, "total_ms": total})
    metrics.inc("requests")
    metrics.inc(f"status_{status}")
    metrics.observe("total_ms", total)
    for stage, ms in stages.items():
        metrics.observe(f"{stage}_ms", ms)


def setup_logging(name="assistant", path=None, stream=None):
    """A logger that writes JSON lines to `stream` (stderr by default), and
    also to a file if `path` is given (`requests.log` in production).

    Example (note): writes one JSON line to the output.
        >>> setup_logging("demo_setup", stream=sys.stdout).info("ready")  # doctest: +SKIP
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handlers = [logging.StreamHandler(stream)] + ([logging.FileHandler(path, encoding="utf-8")] if path else [])
    for h in handlers:
        h.setFormatter(JsonFormatter())
        logger.addHandler(h)
    return logger


if __name__ == "__main__":
    # Three requests through fake stages. In the service: wrap each stage with timed(), call log_request
    # at the end, use setup_logging(path="requests.log"), and add GET /metrics -> m.snapshot().
    log, m = setup_logging(stream=sys.stdout), Metrics()
    for rid, question, slow, status in [("a1b2", "Rappelez-moi au 98 123 456, combien de caution ?", 0.20, "ok"),
                                        ("c3d4", "شنية الوثائق اللازمة؟", 0.10, "ok"),
                                        ("e5f6", "amel@gmail.com: visite samedi ?", 0.35, "error")]:
        stages = {}
        with timed(stages, "retrieve"):
            time.sleep(0.03)
        try:
            with timed(stages, "generate"):
                time.sleep(slow)
                if status == "error":
                    raise TimeoutError("model timeout")
        except TimeoutError:
            pass
        log_request(log, m, rid, question, stages, status)
    print("\nGET /metrics ->")
    print(json.dumps(m.snapshot(), indent=1))
