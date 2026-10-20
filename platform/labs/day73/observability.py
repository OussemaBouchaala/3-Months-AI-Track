# When the agent says "it was slow at 10:42" or "it gave a wrong answer this morning", you need to find that
# request: one JSON log line per request, with its id, stage timings and status, and no personal data.
import json
import logging
import math
import re
import time
from contextlib import contextmanager
from datetime import datetime, timezone

EXTRA_FIELDS = ("request_id", "stage_ms", "status", "question", "n_chunks", "model", "total_ms")
PII = [(re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"), "[EMAIL]"),
       (re.compile(r"(?<!\d)(?:(?:\+|00)216[ .]?)?[2-9]\d(?:[ .]?\d{3}){2}(?!\d)"), "[PHONE]"),
       (re.compile(r"(?<!\d)[01]\d{7}(?!\d)"), "[CIN]")]


def redact(text):
    """Apply every PII pattern in order."""
    # TODO
    ...


class JsonFormatter(logging.Formatter):
    def format(self, record):
        """One JSON object per line: {"ts": UTC ISO time from record.created (seconds precision, ending in "+00:00"),
        "level": record.levelname, "logger": record.name, "msg": redact(record.getMessage())}, plus every
        EXTRA_FIELDS attribute present on the record (extra={...} in the logging call); "question" is redacted too.
        ensure_ascii=False."""
        # TODO
        ...


@contextmanager
def timed(stages, name, clock=time.perf_counter):
    """with timed(stages, "retrieve"): ...  ->  stages["retrieve"] = elapsed milliseconds (int), even if the block raises."""
    # TODO
    yield


class Metrics:
    """In-process counters and latency histograms, exposed at GET /metrics."""

    def __init__(self):
        self.counters, self.values = {}, {}

    def inc(self, name, n=1):
        self.counters[name] = self.counters.get(name, 0) + n

    def observe(self, name, value):
        self.values.setdefault(name, []).append(value)

    def snapshot(self):
        """{"counters": {...}, "histograms": {name: {"count", "p50", "p95", "max"}}} with nearest-rank percentiles."""
        # TODO
        ...


def log_request(logger, metrics, request_id, question, stages, status):
    """Log one INFO line "request" with extra request_id, question, stage_ms=stages, status, total_ms=sum(stages).
    Update metrics: inc("requests"), inc(f"status_{status}"), observe("total_ms", total) and
    observe(f"{stage}_ms", ms) for each stage."""
    # TODO
    ...


def setup_logging(name="assistant", path=None):
    """A logger writing JSON lines to stderr (and to a file if path is given)."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handlers = [logging.StreamHandler()] + ([logging.FileHandler(path, encoding="utf-8")] if path else [])
    for h in handlers:
        h.setFormatter(JsonFormatter())
        logger.addHandler(h)
    return logger


if __name__ == "__main__":
    log, m = setup_logging(path="requests.log"), Metrics()
    stages = {}
    with timed(stages, "retrieve"):
        time.sleep(0.05)
    with timed(stages, "generate"):
        time.sleep(0.2)
    log_request(log, m, "a1b2c3", "Rappelez-moi au 98 123 456, combien de caution ?", stages, "ok")
    print(json.dumps(m.snapshot(), indent=1))
    # In the service: wrap each stage with timed(), call log_request at the end, and add GET /metrics -> m.snapshot().
