sent = {}


class FakeResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return {"message": {"content": '{"city": "Sousse"}'}}


class FakeHttpx:
    """Stands in for httpx while the check calls your chat()."""
    def post(self, url, json=None, timeout=None, **kw):
        sent.update(url=url, body=json, timeout=timeout)
        return FakeResponse()


chat = fn("chat")
real_httpx = chat.__globals__.get("httpx")
chat.__globals__["httpx"] = FakeHttpx()
try:
    result = chat("hello")
finally:
    chat.__globals__["httpx"] = real_httpx

check("chat posts to /api/chat", lambda: sent["url"].endswith("/api/chat"), "httpx.post(f\"{OLLAMA}/api/chat\", json=..., timeout=120)")
check("chat asks for JSON output without streaming",
      lambda: sent["body"]["format"] == "json" and sent["body"]["stream"] is False)
check("chat sends your prompt as a user message",
      lambda: sent["body"]["messages"][0] == {"role": "user", "content": "hello"} and sent["body"]["model"])
check("chat returns (reply_text, seconds)", lambda: result[0] == '{"city": "Sousse"}' and isinstance(result[1], float))

acc = fn("field_accuracy")
label = {"price_tnd": 250000, "surface_m2": 120, "rooms": 3, "city": "Sousse"}
check("field_accuracy is 1.0 when every field matches", lambda: acc(dict(label), label) == 1.0)
check("field_accuracy counts matching fields", lambda: acc({"price_tnd": 250000, "rooms": 4, "city": "Sousse"}, label) == 0.5,
      "Missing fields count as wrong: use pred.get(field).")
