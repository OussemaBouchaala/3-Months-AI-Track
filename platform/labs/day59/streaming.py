"""A 6-second answer feels broken; the same answer appearing word by word after 0.5 s feels fast.

**Server-Sent Events (SSE)**: plain text over one long HTTP response. The server writes
one event per token, then the sources, then "done". The browser's `EventSource` (or a
`fetch` reader) shows each token as it arrives.

An event is a few `field: value` lines followed by an empty line:

    event: token
    id: 0
    data: La

1. `sse_event`: format one event (server side).
2. `parse_sse`: read events back (client side, and tests).
3. `stream_answer`: tokens -> events, with a clean error event.
4. `create_app`: `GET /stream?q=...` as `text/event-stream`.
"""
import json

from fastapi import FastAPI
from fastapi.responses import StreamingResponse


def sse_event(data, event=None, id=None):
    """Format one SSE event.

    Optional `event:` and `id:` lines, then one `data:` line **per line** of
    data (a raw newline inside `data:` would end the field), then an empty
    line that closes the event.

    Example:
        >>> sse_event("hello")
        'data: hello\\n\\n'
        >>> print(sse_event("a\\nb", "token", 3))
        event: token
        id: 3
        data: a
        data: b
        <BLANKLINE>
    """
    lines = []
    if event:
        lines.append(f"event: {event}")
    if id is not None:
        lines.append(f"id: {id}")
    lines += [f"data: {line}" for line in str(data).split("\n")]
    return "\n".join(lines) + "\n\n"


def parse_sse(text):
    """The client side: split the stream into events.

    Events are separated by blank lines. In each block, `line.partition(":")`
    splits `field: value`; one leading space of the value is dropped. Several
    `data` lines are joined with `\\n`. Lines starting with `:` are comments
    (servers send them as keep-alives). An event without `event:` is a
    `"message"`.

    Example:
        >>> parse_sse("event: token\\nid: 0\\ndata: La\\n\\n: keep-alive\\n\\ndata: x\\ndata: y\\n\\n")
        [{'event': 'token', 'id': '0', 'data': 'La'}, {'event': 'message', 'id': None, 'data': 'x\\ny'}]
    """
    events = []
    for block in text.split("\n\n"):
        if not block.strip():
            continue
        ev, data = {"event": "message", "id": None}, []
        for line in block.split("\n"):
            if line.startswith(":"):
                continue
            field, _, value = line.partition(":")
            value = value[1:] if value.startswith(" ") else value
            if field == "data":
                data.append(value)
            elif field in ("event", "id"):
                ev[field] = value
        if data:
            events.append(dict(ev, data="\n".join(data)))
    return events


def stream_answer(tokens, sources):
    """A generator of SSE events for one answer.

    1. One `token` event per token, with `id` 0, 1, 2... (a client can tell
       if it missed one).
    2. A `sources` event with the sources as JSON.
    3. A `done` event with `[DONE]`, so the client knows to stop listening.

    If the model fails mid-answer, the HTTP status is already 200 (headers
    were sent with the first token), so the failure must travel **as an
    event**: `error`, and no sources/done.

    Example:
        >>> for e in stream_answer(iter(["Deux ", "mois"]), [{"n": 1, "id": "reg-c2"}]):
        ...     print(repr(e))
        'event: token\\nid: 0\\ndata: Deux \\n\\n'
        'event: token\\nid: 1\\ndata: mois\\n\\n'
        'event: sources\\ndata: [{"n": 1, "id": "reg-c2"}]\\n\\n'
        'event: done\\ndata: [DONE]\\n\\n'
    """
    try:
        for i, tok in enumerate(tokens):
            yield sse_event(tok, "token", i)
    except Exception:
        yield sse_event("generation failed", "error")
        return
    yield sse_event(json.dumps(sources, ensure_ascii=False), "sources")
    yield sse_event("[DONE]", "done")


def create_app(retrieve, generate_stream):
    """`GET /stream?q=...&k=5` streams the answer.

    - `retrieve(q, k)` -> chunks; `generate_stream(q, chunks)` -> an iterator
      of text tokens (with Ollama or Claude: `stream=True`).
    - `StreamingResponse` sends each yielded string as soon as it's ready.
    - `Cache-Control: no-cache` and `X-Accel-Buffering: no` stop proxies
      (nginx) from holding tokens back and sending them all at the end.

    Example:
        >>> from fastapi.testclient import TestClient
        >>> app = create_app(lambda q, k: [{"id": "reg-c2"}], lambda q, chunks: iter(["Deux ", "mois ", "[1]."]))
        >>> r = TestClient(app).get("/stream", params={"q": "caution"})
        >>> r.headers["content-type"]
        'text/event-stream; charset=utf-8'
        >>> [(e["event"], e["data"]) for e in parse_sse(r.text)]
        [('token', 'Deux '), ('token', 'mois '), ('token', '[1].'), ('sources', '[{"n": 1, "id": "reg-c2"}]'), ('done', '[DONE]')]
    """
    app = FastAPI(title="Streaming answers")

    @app.get("/stream")
    def stream(q: str, k: int = 5):
        chunks = retrieve(q, k)
        sources = [{"n": i, "id": c["id"]} for i, c in enumerate(chunks, 1)]
        return StreamingResponse(stream_answer(generate_stream(q, chunks), sources), media_type="text/event-stream",
                                 headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    return app


def fake_tokens(q, chunks):
    """A fake model that yields one word every 0.15 s, like a real stream.

    Example:
        >>> "".join(fake_tokens("caution", []))
        'La caution est de deux mois de loyer [1]. '
    """
    import time
    for w in "La caution est de deux mois de loyer [1].".split(" "):
        time.sleep(0.15)
        yield w + " "


def serve():
    """Run the streaming server for your browser on port 8000.

    Open http://127.0.0.1:8000/stream?q=caution, or `curl -N` it: you'll see
    the words arrive one by one.

    Note: starts a server that runs until you stop it.
    """
    import uvicorn
    uvicorn.run(create_app(lambda q, k: [{"id": "reg-c2"}], fake_tokens), port=8000)


if __name__ == "__main__":
    import sys
    import time
    if "--serve" in sys.argv:
        serve()
    else:
        # Demo 1: what the server sends, and when (each event leaves as soon as its token exists).
        t0, shown = time.perf_counter(), ""
        for raw in stream_answer(fake_tokens("caution", []), [{"n": 1, "id": "reg-c2"}]):
            e = parse_sse(raw)[0]
            shown += e["data"] if e["event"] == "token" else ""
            print(f"{time.perf_counter() - t0:5.2f}s  {e['event']:8} {e['data']!r}")
        print("\nthe user saw:", shown)

        # Demo 2: the real endpoint, through a test client (it collects the whole stream).
        from fastapi.testclient import TestClient
        r = TestClient(create_app(lambda q, k: [{"id": "reg-c2"}], lambda q, c: iter(["Deux ", "mois."]))).get("/stream", params={"q": "caution"})
        print("\nGET /stream ->", r.headers["content-type"], [e["event"] for e in parse_sse(r.text)])

        def broken(q, chunks):
            yield "La "
            raise TimeoutError("model")
        print("\nmodel crash mid-answer:", [e["event"] for e in parse_sse("".join(stream_answer(broken("q", []), [])))])
