import httpx

resp = httpx.post("http://localhost:11434/api/chat", json={
    "model": "qwen2.5:3b",
    "messages": [{"role": "user", "content": "Return {\"ok\": true} as JSON."}],
    "format": "json",
    "stream": False,
}, timeout=120)
print(resp.json()["message"]["content"])
