# Week 8's pieces behind one HTTP endpoint. The retriever and the model are passed in (dependency injection):
# the real ones in production, fakes in tests, so the service is testable without Postgres or Ollama.
import re
import time
import uuid

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

IDK = "I don't know based on the documents."


class AskIn(BaseModel):
    question: str = Field(min_length=2, max_length=1000)
    k: int = Field(default=5, ge=1, le=20)


def build_prompt(question, chunks):
    """The Day 18 prompt: numbered sources "[1] title > section\\ntext", answer only from them, cite [n],
    reply exactly IDK when the sources don't answer, answer in the question's language."""
    # TODO
    ...


def create_app(retrieve, generate, scrub=lambda text: text):
    """retrieve(question, k) -> chunks [{"id", "doc_id", "title", "section", "text"}]; generate(prompt) -> str;
    scrub(text) -> masked text (Week 7's PII scrubber)."""
    app = FastAPI(title="Project assistant")

    @app.middleware("http")
    async def request_id(request: Request, call_next):
        """Echo the X-Request-ID header, or create one (uuid4 hex), on every response."""
        # TODO
        return await call_next(request)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/ask")
    def ask(body: AskIn):
        """1. scrub the question. 2. retrieve(question, k). 3. No chunks -> IDK without calling the model.
        4. generate(build_prompt(...)); any exception -> HTTP 503 "model unavailable".
        5. Rewrite "[1, 2]" as "[1][2]", then drop citation markers [n] outside 1..len(chunks).
        Return {"answer", "idk": bool, "sources": [{"n", "id", "doc_id", "title", "section"}] for the cited n's in order,
        "latency_ms": int}."""
        # TODO
        ...

    return app


def real_app():
    """Production wiring: vector search over project_chunks (day53) + the Bench model + the PII scrubber."""
    import sys
    sys.path += ["../day16", "../day17", "../day45"]
    import psycopg
    from bench_llm import current_model, get_client
    from embed import embed
    from pg_store import DSN, to_vector_literal
    from pii_scrub import scrub

    conn = psycopg.connect(DSN, autocommit=True)
    client = get_client()

    def retrieve(question, k):
        vec = to_vector_literal(embed([question])[0])
        rows = conn.execute("SELECT id, doc_id, section, text FROM project_chunks ORDER BY embedding <=> %s::vector LIMIT %s", (vec, k)).fetchall()
        return [{"id": r[0], "doc_id": r[1], "title": r[1], "section": r[2], "text": r[3]} for r in rows]

    def generate(prompt):
        msg = client.messages.create(model=current_model(), max_tokens=600, temperature=0, messages=[{"role": "user", "content": prompt}])
        return msg.content[0].text

    return create_app(retrieve, generate, scrub=lambda t: scrub(t)[0])


if __name__ == "__main__":
    # Needs Postgres (day17) with project_chunks (day53) and Ollama. Then open http://127.0.0.1:8000/docs
    # (or: uvicorn pipeline_service:real_app --factory --reload)
    import uvicorn
    uvicorn.run(real_app(), port=8000)
