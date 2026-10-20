# A 6-second answer feels broken; the same answer appearing word by word after 0.5 s feels fast.
# Server-Sent Events (SSE): plain text over HTTP, one event per token, then the sources, then "done".
import json

from fastapi import FastAPI
from fastapi.responses import StreamingResponse


def sse_event(data, event=None, id=None):
    """Format one SSE event. Optional "event: <name>" and "id: <id>" lines, then one "data: " line per line of data
    (data may contain newlines), then an empty line. Example: sse_event("a\\nb", "token") == "event: token\\ndata: a\\ndata: b\\n\\n"."""
    # TODO
    ...


def parse_sse(text):
    """The client side: split on blank lines, read event/id/data fields (data lines joined with "\\n").
    Return [{"event": name or "message", "id": id or None, "data": str}]. Ignore lines starting with ":" (comments)."""
    # TODO
    ...


def stream_answer(tokens, sources):
    """Yield: one "token" event per token (data = the token, id = 0, 1, 2...), then a "sources" event with
    json.dumps(sources, ensure_ascii=False), then a "done" event with data "[DONE]".
    If the token iterator raises, yield an "error" event with data "generation failed" and stop."""
    # TODO
    ...


def create_app(retrieve, generate_stream):
    """retrieve(q, k) -> chunks; generate_stream(q, chunks) -> iterator of text tokens."""
    app = FastAPI(title="Streaming answers")

    @app.get("/stream")
    def stream(q: str, k: int = 5):
        """StreamingResponse(stream_answer(...), media_type="text/event-stream") with headers
        Cache-Control: no-cache and X-Accel-Buffering: no (so proxies don't hold the tokens back).
        Sources: [{"n": i, "id": chunk id}] for the retrieved chunks, numbered from 1."""
        # TODO
        ...

    return app


if __name__ == "__main__":
    import time
    import uvicorn

    def fake_tokens(q, chunks):
        for w in "La caution est de deux mois de loyer [1].".split(" "):
            time.sleep(0.15)
            yield w + " "

    app = create_app(lambda q, k: [{"id": "reg-c2"}], fake_tokens)
    print("Open http://127.0.0.1:8000/stream?q=caution in the browser, or: curl -N 'http://127.0.0.1:8000/stream?q=caution'")
    uvicorn.run(app, port=8000)
