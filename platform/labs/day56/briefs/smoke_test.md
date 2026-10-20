# Smoke test
**Topic:** a few real questions through the running service, with an exit code, so "it works" is a command, not a feeling.

## Real example
A shop checking its website after each deploy (different service, same idea):

```python
pages = {"/": (200, "Welcome"), "/cart": (200, "Your cart"), "/pay": (502, "")}
fails = []
for path, (status, text) in pages.items():
    if status != 200:
        fails.append(f"{path}: status {status}")
    elif not text:
        fails.append(f"{path}: empty page")
print(f"{len(pages) - len(fails)}/{len(pages)} ok", fails)
print("exit code:", 1 if fails else 0)
```

The exit code matters: in Week 11, CI runs this after `docker compose up` and stops a broken release.

## Your mission
End Week 8 with a one-command check of the whole path: question, retrieval, model, citations.

## Steps
1. `check_case` with all its rules.
2. `run_smoke` (exceptions are failures), `summary`, `exit_code`.
3. Edit `CASES`: 6 or more from your golden dev set, with at least one `idk`.
4. Start the service (day55), then **Run** this file.

## Done when
**Check** passes and the smoke test passes against your running service.
