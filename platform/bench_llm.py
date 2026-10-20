"""One small LLM client for everything in Bench: your labs, and the AI tutor.

Pick a provider once in Bench (AI settings, the gear in the header). Free options:
    gemini      free API key from https://aistudio.google.com/apikey
    groq        free API key from https://console.groq.com/keys
    openrouter  free API key from https://openrouter.ai/keys  (models ending in ":free")
    ollama      runs open models on your own computer, no key at all (https://ollama.com)
Paid: anthropic.

The settings live in bench/llm_settings.local.json (git ignores it), so you never
have to set environment variables or restart anything.

In a lab:
    from bench_llm import get_client, current_model
    client = get_client()
    msg = client.messages.create(model=current_model(), max_tokens=200, system="...",
                                 temperature=0.0, messages=[{"role": "user", "content": "hi"}])
    msg.content[0].text, msg.usage.input_tokens, msg.usage.output_tokens

Only the standard library is used, so nothing to pip install.
"""
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from types import SimpleNamespace

SETTINGS_FILE = Path(__file__).resolve().parent / "llm_settings.local.json"

PROVIDERS = {
    "gemini": {
        "label": "Google Gemini (free key)",
        "base": "https://generativelanguage.googleapis.com/v1beta/openai",
        "model": "gemini-2.5-flash",
        "key_url": "https://aistudio.google.com/apikey",
        "needs_key": True,
    },
    "groq": {
        "label": "Groq (free key, open models, very fast)",
        "base": "https://api.groq.com/openai/v1",
        "model": "qwen/qwen3.8-27b",
        "key_url": "https://console.groq.com/keys",
        "needs_key": True,
    },
    "openrouter": {
        "label": "OpenRouter (free key, pick a ':free' model)",
        "base": "https://openrouter.ai/api/v1",
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        "key_url": "https://openrouter.ai/keys",
        "needs_key": True,
    },
    "ollama": {
        "label": "Ollama (open source, on your computer, no key)",
        "base": "http://localhost:11434/v1",
        "model": "qwen2.5:3b",
        "key_url": "https://ollama.com/download",
        "needs_key": False,
    },
    "anthropic": {
        "label": "Anthropic Claude (paid credits)",
        "base": "https://api.anthropic.com/v1",
        "model": "claude-haiku-4-5",
        "key_url": "https://console.anthropic.com/settings/keys",
        "needs_key": True,
    },
}


class LLMError(RuntimeError):
    """A readable error: what went wrong and what to do about it."""


# ---------------------------------------------------------------- settings
def load_settings():
    data = {}
    try:
        data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        pass
    data.setdefault("provider", "")
    data.setdefault("keys", {})
    data.setdefault("models", {})
    # Environment variables still work, and win, for people who prefer them.
    for env, prov in (("GEMINI_API_KEY", "gemini"), ("GROQ_API_KEY", "groq"),
                      ("OPENROUTER_API_KEY", "openrouter"), ("ANTHROPIC_API_KEY", "anthropic")):
        if os.environ.get(env):
            data["keys"][prov] = os.environ[env]
    if os.environ.get("LLM_PROVIDER"):
        data["provider"] = os.environ["LLM_PROVIDER"]
    if not data["provider"]:
        data["provider"] = next((p for p in ("gemini", "groq", "openrouter", "anthropic") if data["keys"].get(p)), "")
    return data


def save_settings(data):
    clean = {"provider": data.get("provider", ""),
             "keys": {k: v for k, v in (data.get("keys") or {}).items() if v},
             "models": {k: v for k, v in (data.get("models") or {}).items() if v}}
    SETTINGS_FILE.write_text(json.dumps(clean, indent=2), encoding="utf-8")
    return clean


def current_provider():
    p = load_settings()["provider"]
    if p not in PROVIDERS:
        raise LLMError("No AI provider chosen yet. In Bench, click the gear (AI settings) in the header, "
                       "pick a free provider such as Google Gemini, paste its key and press Save.")
    return p


def current_model(provider=None):
    s = load_settings()
    provider = provider or current_provider()
    return s["models"].get(provider) or PROVIDERS[provider]["model"]


# ---------------------------------------------------------------- HTTP
def _request(url, payload=None, headers=None, timeout=90):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method="POST" if data else "GET",
                                 headers={"Content-Type": "application/json", "Accept": "application/json",
                                          # Cloudflare (Groq, OpenRouter) blocks the default "Python-urllib" agent: error 1010
                                          "User-Agent": "Bench/1.0 (learning platform; +https://github.com/OussemaBouchaala)",
                                          **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            j = json.loads(body)
            j = j[0] if isinstance(j, list) and j else j
            err = j.get("error", j)
            msg = err.get("message", body) if isinstance(err, dict) else str(err)
        except ValueError:
            msg = body
        raise _friendly(e.code, msg[:600]) from None
    except urllib.error.URLError as e:
        if "localhost" in url or "127.0.0.1" in url:
            raise LLMError("Can't reach Ollama on this computer. Install it from https://ollama.com/download, "
                           "open it (or run `ollama serve`), then `ollama pull qwen2.5:3b`.") from None
        raise LLMError(f"Can't reach {url.split('/')[2]}: {e.reason}. Check your internet connection.") from None
    except TimeoutError:
        raise LLMError("The model took too long to answer (timeout). Try again or pick a smaller model.") from None


def _friendly(code, msg):
    low = msg.lower()
    if "1010" in low or "1020" in low:
        return LLMError(f"The provider's firewall blocked the request ({code}, {msg}). Update Bench and try again; "
                        "if it persists, switch provider in AI settings.")
    if code in (401, 403) or "api key" in low or "api_key" in low:
        return LLMError(f"The provider rejected your API key ({code}). Copy it again into AI settings. Details: {msg}")
    if code == 429:
        return LLMError(f"Rate limit reached ({code}): free tiers allow a few requests per minute. "
                        f"Wait a minute and try again. Details: {msg}")
    if code == 404 or "not found" in low:
        return LLMError(f"Model not found ({code}). In AI settings press 'List models' and pick one. Details: {msg}")
    if "credit" in low or "billing" in low or "quota" in low:
        return LLMError(f"This account has no credits or quota left ({code}). Switch to a free provider in AI settings. "
                        f"Details: {msg}")
    return LLMError(f"The provider returned an error ({code}): {msg}")


# ---------------------------------------------------------------- core call
def chat(messages, system=None, temperature=None, max_tokens=800, model=None, provider=None):
    """Send a conversation, get (text, tokens_in, tokens_out) back. Works with every provider."""
    s = load_settings()
    provider = provider or current_provider()
    cfg = PROVIDERS[provider]
    key = s["keys"].get(provider, "")
    if cfg["needs_key"] and not key:
        raise LLMError(f"No API key saved for {cfg['label']}. Get one at {cfg['key_url']} "
                       "and paste it in Bench > AI settings.")
    model = model or current_model(provider)

    if provider == "anthropic":
        payload = {"model": model, "max_tokens": max_tokens, "messages": messages}
        if system:
            payload["system"] = system
        if temperature is not None:
            payload["temperature"] = temperature
        r = _request(cfg["base"] + "/messages", payload,
                     {"x-api-key": key, "anthropic-version": "2023-06-01"})
        text = "".join(b.get("text", "") for b in r.get("content", []) if b.get("type") == "text")
        u = r.get("usage", {})
        return text, u.get("input_tokens", 0), u.get("output_tokens", 0)

    # Everyone else speaks the OpenAI "chat completions" format.
    msgs = ([{"role": "system", "content": system}] if system else []) + list(messages)
    payload = {"model": model, "messages": msgs, "max_tokens": max_tokens}
    if temperature is not None:
        payload["temperature"] = temperature
    headers = {"Authorization": f"Bearer {key or 'ollama'}"}
    if provider == "gemini" and "2.5" in model:
        # Gemini 2.5 "thinks" before answering and those hidden tokens eat max_tokens.
        payload["reasoning_effort"] = "none" if "flash" in model else "low"
    if "gpt-oss" in model:
        # Reasoning model: it thinks first, and those hidden tokens count against max_tokens.
        payload["reasoning_effort"] = "low"
        payload["max_tokens"] = max(max_tokens, 1024)
    try:
        r = _request(cfg["base"] + "/chat/completions", payload, headers)
    except LLMError as e:
        if "reasoning" not in str(e).lower() or "reasoning_effort" not in payload:
            raise
        payload.pop("reasoning_effort")
        payload["max_tokens"] = max(max_tokens, 2048)
        r = _request(cfg["base"] + "/chat/completions", payload, headers)
    choice = (r.get("choices") or [{}])[0]
    text = (choice.get("message") or {}).get("content") or ""
    if "<think>" in text:  # some open models show their reasoning: keep only the answer
        text = text.split("</think>")[-1].strip()
    u = r.get("usage") or {}
    return text, u.get("prompt_tokens", 0), u.get("completion_tokens", 0)


def list_models(provider=None):
    s = load_settings()
    provider = provider or current_provider()
    cfg = PROVIDERS[provider]
    key = s["keys"].get(provider, "")
    if provider == "anthropic":
        r = _request(cfg["base"] + "/models", headers={"x-api-key": key, "anthropic-version": "2023-06-01"})
    else:
        r = _request(cfg["base"] + "/models", headers={"Authorization": f"Bearer {key or 'ollama'}"})
    ids = [m.get("id", "").removeprefix("models/") for m in r.get("data", [])]
    if provider == "openrouter":
        ids = [i for i in ids if i.endswith(":free")] or ids
    if provider == "gemini":
        ids = [i for i in ids if "gemini" in i and "embedding" not in i and "tts" not in i and "image" not in i] or ids
    # Keep chat models only: drop speech, moderation and embedding models.
    skip = ("whisper", "tts", "guard", "orpheus", "playai", "embed", "distil")
    ids = [i for i in ids if not any(k in i.lower() for k in skip)] or ids
    return sorted(set(i for i in ids if i))


# ---------------------------------------------------------------- Anthropic-shaped client
class _Messages:
    def create(self, model=None, max_tokens=800, messages=None, system=None, temperature=None, **_ignored):
        provider = current_provider()
        # A Claude model name only means something to Anthropic; elsewhere use the model from settings.
        if not model or model == "auto" or (provider != "anthropic" and model.startswith("claude")):
            model = None
        text, tin, tout = chat(messages or [], system=system, temperature=temperature,
                               max_tokens=max_tokens, model=model, provider=provider)
        return SimpleNamespace(content=[SimpleNamespace(type="text", text=text)],
                               usage=SimpleNamespace(input_tokens=tin, output_tokens=tout),
                               model=model or current_model(provider))


class Client:
    """Looks like anthropic.Anthropic(): client.messages.create(...). Uses the provider from AI settings."""

    def __init__(self):
        self.messages = _Messages()


def get_client():
    current_provider()  # fail early with a helpful message
    return Client()


if __name__ == "__main__":
    p = current_provider()
    print("provider:", p, " model:", current_model(p))
    print(chat([{"role": "user", "content": "Say hello in Tunisian Arabic, one line."}], temperature=0))
