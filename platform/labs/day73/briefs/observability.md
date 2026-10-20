# Logs and metrics
**Topic:** structured JSON logs per request, stage timings, simple metrics, and no personal data in any of it.

## Real example
Why JSON lines beat free text when something goes wrong (a different service's logs):

```python
import json
lines = ['{"request_id": "r1", "status": "ok", "total_ms": 820}',
         '{"request_id": "r2", "status": "error", "total_ms": 15000}',
         '{"request_id": "r3", "status": "ok", "total_ms": 7600}']
rows = [json.loads(l) for l in lines]
print("slow:", [r["request_id"] for r in rows if r["total_ms"] > 5000])
print("errors:", [r["request_id"] for r in rows if r["status"] != "ok"])
```

"Find the slow requests" becomes one line of code instead of reading log text by eye.

## Your mission
Make every request of your service findable and measurable.

## Steps
1. `redact`, then `JsonFormatter.format` (redact the message and the question).
2. `timed`: a context manager that records milliseconds even on errors.
3. `Metrics.snapshot` and `log_request`.
4. In your service: time each stage, log once per request with the request id, expose `GET /metrics`.

## Done when
**Check** passes and `requests.log` has one JSON line per question, with no phone number in it.
