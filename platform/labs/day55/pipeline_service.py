"""Week 8's pieces behind one HTTP endpoint: `POST /ask`.

The retriever and the model are **passed in** (dependency injection): the real ones in
production, fakes in tests. So the whole service is testable without Postgres or Ollama.

1. `AskIn`: what a request must look like (validated by pydantic).
2. `build_prompt`: Day 18's grounded prompt with numbered sources.
3. `fix_citations` and `cited_sources`: clean markers, list what was cited.
4. `create_app`: the FastAPI app (request id, /health, /ask).
5. `real_app`: the production wiring.
"""
import re
import time
import uuid

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

IDK = "I don't know based on the documents."


class AskIn(BaseModel):
    """The body of `POST /ask`. FastAPI rejects anything else with a 422.

    `Field(min_length=2, max_length=1000)` refuses an empty or huge question;
    `k` (how many chunks to retrieve) must be between 1 and 20, 5 by default.

    Example:
        >>> AskIn(question="Caution ?")
        AskIn(question='Caution ?', k=5)
        >>> try:
        ...     AskIn(question="Caution ?", k=50)
        ... except Exception as e:
        ...     print(type(e).__name__)
        ValidationError
    """
    question: str = Field(min_length=2, max_length=1000)
    k: int = Field(default=5, ge=1, le=20)


def build_prompt(question, chunks):
    """The Day 18 prompt: numbered sources, then the rules, then the question.

    Each source is `[n] title > section` on one line and its text below.
    The rules: answer only from the sources, cite every fact as `[n]`,
    reply exactly `IDK` when the sources don't answer, and answer in the
    question's language (a Derja question gets a Derja answer).

    Example:
        >>> chunks = [{"title": "Règlement", "section": "Caution", "text": "Deux mois de loyer."},
        ...           {"title": "FAQ", "section": "", "text": "Un demi-mois en plus avec un animal."}]
        >>> print(build_prompt("Caution ?", chunks).split("Sources:")[1])
        <BLANKLINE>
        [1] Règlement > Caution
        Deux mois de loyer.
        <BLANKLINE>
        [2] FAQ
        Un demi-mois en plus avec un animal.
        <BLANKLINE>
        Question: Caution ?
    """
    sources = "\n\n".join(f"[{i}] {c['title']}{' > ' + c['section'] if c.get('section') else ''}\n{c['text']}" for i, c in enumerate(chunks, 1))
    return ("Answer using ONLY the sources below. Cite every fact with its source number, like [1]. "
            f"If the sources don't contain the answer, reply exactly: {IDK} Answer in the language of the question.\n\n"
            f"Sources:\n{sources}\n\nQuestion: {question}")


def fix_citations(text, n_sources):
    """Day 54's cleanup, inline: `[1, 2]` -> `[1][2]`, then drop markers
    outside `1..n_sources`.

    Example:
        >>> fix_citations("Deux mois [1, 7]. Un chat [2].", 2)
        'Deux mois [1]. Un chat [2].'
    """
    text = re.sub(r"\[(\d+(?:\s*,\s*\d+)+)\]", lambda m: "".join(f"[{n.strip()}]" for n in m.group(1).split(",")), text)
    return re.sub(r"\[(\d+)\]", lambda m: m.group() if 1 <= int(m.group(1)) <= n_sources else "", text)


def cited_sources(text, chunks):
    """The cited chunks, in the order first cited, with their number `n`.

    The front end shows these as links under the answer; only cited ones,
    not all 5 retrieved.

    Example:
        >>> chunks = [{"id": "reg-c0", "doc_id": "reg", "title": "R", "section": "Caution"}, {"id": "faq-c3", "doc_id": "faq", "title": "FAQ"}]
        >>> cited_sources("A [2]. B [1][2].", chunks)
        [{'n': 2, 'id': 'faq-c3', 'doc_id': 'faq', 'title': 'FAQ', 'section': ''}, {'n': 1, 'id': 'reg-c0', 'doc_id': 'reg', 'title': 'R', 'section': 'Caution'}]
    """
    cited = list(dict.fromkeys(int(n) for n in re.findall(r"\[(\d+)\]", text)))
    return [{"n": n, **{k: chunks[n - 1].get(k, "") for k in ("id", "doc_id", "title", "section")}} for n in cited]


def create_app(retrieve, generate, scrub=lambda text: text):
    """Build the FastAPI app around three functions you pass in.

    - `retrieve(question, k)` -> chunks `[{"id", "doc_id", "title", "section", "text"}]`
    - `generate(prompt)` -> the model's text
    - `scrub(text)` -> masked text (Week 7's PII scrubber)

    Inside:

    - A **middleware** runs around every request: it echoes the
      `X-Request-ID` header or creates one (`uuid4().hex`), so one request
      can be followed through all the logs.
    - `GET /health` answers `{"status": "ok"}` for monitors.
    - `POST /ask`: scrub -> retrieve -> no chunks? IDK without calling the
      model -> generate (a model error becomes HTTP **503**, "try later",
      not a 500 crash) -> clean citations -> answer, idk, sources, latency.

    Example (fakes instead of Postgres and the model):
        >>> from fastapi.testclient import TestClient
        >>> chunks = [{"id": "reg-c0", "doc_id": "reg", "title": "Règlement", "section": "Caution", "text": "Deux mois."}]
        >>> app = create_app(lambda q, k: chunks if "caution" in q else [], lambda prompt: "Deux mois [1, 3].")
        >>> client = TestClient(app)
        >>> r = client.post("/ask", json={"question": "Combien de caution ?"}).json()
        >>> r["answer"], r["idk"], [s["id"] for s in r["sources"]]
        ('Deux mois [1].', False, ['reg-c0'])
        >>> client.post("/ask", json={"question": "Une voiture ?"}).json()["answer"]
        "I don't know based on the documents."
    """
    app = FastAPI(title="Project assistant")

    @app.middleware("http")
    async def request_id(request: Request, call_next):
        rid = request.headers.get("x-request-id") or uuid.uuid4().hex
        response = await call_next(request)
        response.headers["X-Request-ID"] = rid
        return response

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/ask")
    def ask(body: AskIn):
        t0 = time.perf_counter()
        question = scrub(body.question)
        chunks = retrieve(question, body.k)
        if not chunks:
            return {"answer": IDK, "idk": True, "sources": [], "latency_ms": int((time.perf_counter() - t0) * 1000)}
        try:
            text = generate(build_prompt(question, chunks)).strip()
        except Exception:
            raise HTTPException(503, detail="model unavailable")
        text = fix_citations(text, len(chunks))
        return {"answer": text, "idk": IDK in text, "sources": cited_sources(text, chunks),
                "latency_ms": int((time.perf_counter() - t0) * 1000)}

    return app


def real_app():
    """Production wiring: vector search over `project_chunks` (day 53), the
    Bench model, and the PII scrubber (day 45).

    Start it with `python pipeline_service.py --serve`, or
    `uvicorn pipeline_service:real_app --factory --reload`, then open
    http://127.0.0.1:8000/docs. Needs Postgres (day 17) and Ollama.

    Example (note): needs Postgres, Ollama and your index.
        >>> app = real_app()  # doctest: +SKIP
    """
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
    import sys
    if "--serve" in sys.argv:
        import uvicorn
        uvicorn.run(real_app(), port=8000)
    else:
        # Demo: the real app code with a fake retriever and a fake model, called through a test client.
        from fastapi.testclient import TestClient
        CHUNKS = [{"id": "reg-c0", "doc_id": "reglement", "title": "Règlement", "section": "Caution", "text": "Deux mois de loyer."},
                  {"id": "faq-c3", "doc_id": "faq", "title": "FAQ", "section": "", "text": "Un demi-mois en plus avec un animal."}]

        def retrieve(q, k):
            return [] if "voiture" in q else CHUNKS[:k]

        def generate(prompt):
            if "PANNE" in prompt:
                raise RuntimeError("ollama down")
            return "La caution est de deux mois [1, 7]. Plus un demi-mois avec un chat [2]."

        client = TestClient(create_app(retrieve, generate, scrub=lambda t: t.replace("98123456", "[PHONE_1]")))
        print("GET /health ->", client.get("/health").json())
        for q in ["Combien de caution avec un chat ?", "Vous vendez une voiture ?", "PANNE: rappelez le 98123456", ""]:
            r = client.post("/ask", json={"question": q}, headers={"X-Request-ID": "demo-1"})
            body = r.json()
            print(f"\nPOST /ask {q!r} -> {r.status_code} (request id {r.headers['x-request-id']})")
            if r.status_code == 200:
                print("  answer: ", body["answer"])
                print("  sources:", [f"[{s['n']}] {s['title']}" for s in body["sources"]])
            else:
                print("  detail: ", str(body["detail"])[:90])
