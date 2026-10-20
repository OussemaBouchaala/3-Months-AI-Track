# The README that gets read
**Topic:** problem, architecture, results, one-command run, next steps.

## Real example
The top of a README that a recruiter actually reads (results come early):

```markdown
# Invoice reader
Turns scanned supplier invoices into clean JSON (supplier, date, total, VAT).

**Results (50 invoices):** field accuracy 0.94 · p95 latency 1.8 s · $0.30 per 1k invoices

## Run it
docker compose up --build   # then POST a PDF to http://localhost:8000/extract

## Architecture
PDF -> OCR -> LLM (JSON schema) -> Pydantic validation (1 retry) -> API
```

## Your mission
Replace every TODO comment with real content.

## Steps
1. Problem and Architecture in 2-3 lines each.
2. Paste the table from `day12/results.md` under Results.
3. Three bullet points under "What I'd improve".

## Done when
**Check** finds every section written and the results table.
