# LLM Extraction Service

Messy real estate listings (Arabic, French, English) in, clean validated JSON out.

## Problem
<!-- TODO: 2-3 sentences: who has this problem, and why free text isn't enough -->
> Real estate agencies and data-platform devs need structured fields (city, area, price, language) from messy, multilingual (Arabic/French/English) listings. Regex or rule-based parsers break on inconsistent formatting and mixed scripts, so an LLM-based extractor with JSON-schema validation gives far higher field accuracy.

## Architecture
<!-- TODO: a small diagram or list: client -> FastAPI /extract -> Ollama or API model -> Pydantic validation (1 retry) -> JSON -->
client -> FastAPI /extract -> Ollama or API model -> Pydantic validation (1 retry) -> JSON
## Results
<!-- TODO: paste the table from day12/results.md -->
| model | field accuracy | p50 latency (s) | p95 latency (s) | cost per 1k requests |
|---|---|---|---|---|
| api | 0.10 | 0.29 | 0.31 | $1.20 |
| local | 0.78 | 4.62 | 10.21 | local hardware |

## Run it
```bash
docker compose up --build
docker compose exec ollama ollama pull qwen2.5:3b
curl -X POST localhost:8002/extract -H "Content-Type: application/json" -d '{"text": "S+2 95m2 Sousse 280 000 DT"}'
```

## What I'd improve
<!-- TODO: 3 bullet points -->
- Add a second retry with a different prompt for fields the LLM left null or misfilled (improved field accuracy on garbled text).
- Cache identical requests (same text hash) to cut latency and cost for highly repeated listing snippets.
- Swap the local model for a mid-size one (e.g., 7B) once hardware allows, or use API for high-accuracy batches and local for bulk, balancing quality vs. cost.