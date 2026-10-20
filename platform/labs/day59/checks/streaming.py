import json
from fastapi.testclient import TestClient
se = fn("sse_event")
check("sse_event: data only", lambda: se("hello") == "data: hello\n\n")
check("sse_event: event, id, multi-line data", lambda: se("a\nb", "token", 3) == "event: token\nid: 3\ndata: a\ndata: b\n\n")
ps = fn("parse_sse")
check("parse_sse reads events back", lambda: ps("event: token\nid: 0\ndata: La\n\ndata: x\ndata: y\n\n") == [{"event": "token", "id": "0", "data": "La"}, {"event": "message", "id": None, "data": "x\ny"}])
check("parse_sse ignores comments and empty blocks", lambda: ps(": keep-alive\n\n\n\nevent: done\ndata: [DONE]\n\n") == [{"event": "done", "id": None, "data": "[DONE]"}])
sa = fn("stream_answer")
evs = lambda toks: ps("".join(sa(toks, [{"n": 1, "id": "reg-c2"}])))
check("stream_answer: tokens with ids, then sources, then done", lambda: [(e["event"], e["data"]) for e in evs(iter(["La ", "caution"]))] == [("token", "La "), ("token", "caution"), ("sources", '[{"n": 1, "id": "reg-c2"}]'), ("done", "[DONE]")] and evs(iter(["a", "b"]))[1]["id"] == "1")
def broken():
    yield "La "
    raise TimeoutError("model")
check("a failure mid-stream becomes an error event, no sources/done", lambda: [e["event"] for e in evs(broken())] == ["token", "error"])
create_app = fn("create_app")
def _get():
    app = create_app(lambda q, k: [{"id": f"c{i}"} for i in range(k)], lambda q, chunks: iter(["Deux ", "mois ", "[1]."]))
    return TestClient(app).get("/stream", params={"q": "caution", "k": 2})
check("GET /stream is text/event-stream with no-cache", lambda: _get().headers["content-type"].startswith("text/event-stream") and _get().headers.get("cache-control") == "no-cache")
check("the stream carries tokens and numbered sources", lambda: (lambda e: "".join(x["data"] for x in e if x["event"] == "token") == "Deux mois [1]." and json.loads([x for x in e if x["event"] == "sources"][0]["data"]) == [{"n": 1, "id": "c0"}, {"n": 2, "id": "c1"}])(ps(_get().text)))
