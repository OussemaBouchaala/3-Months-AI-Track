# LLM Extraction Service

Messy real estate listings (Arabic, French, English) in, clean validated JSON out.

## Problem
<!-- TODO: 2-3 sentences: who has this problem, and why free text isn't enough -->

## Architecture
<!-- TODO: a small diagram or list: client -> FastAPI /extract -> Ollama or API model -> Pydantic validation (1 retry) -> JSON -->

## Results
<!-- TODO: paste the table from day12/results.md -->

## Run it
```bash
docker compose up --build
docker compose exec ollama ollama pull qwen2.5:3b
curl -X POST localhost:8002/extract -H "Content-Type: application/json" -d '{"text": "S+2 95m2 Sousse 280 000 DT"}'
```

## What I'd improve
<!-- TODO: 3 bullet points -->
