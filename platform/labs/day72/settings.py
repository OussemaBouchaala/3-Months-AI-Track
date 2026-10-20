# Hard-coded "localhost:5432" and an API key in the code work on your laptop and nowhere else.
# One settings module: typed values from the environment, a .env file for local dev, defaults,
# ALL missing values reported at once, and secrets never printed.
import os
from pathlib import Path

REQUIRED = object()
FIELDS = {   # name: (type, default, secret)
    "DATABASE_URL": (str, REQUIRED, True),
    "OLLAMA_URL": (str, "http://localhost:11434", False),
    "LLM_PROVIDER": (str, "ollama", False),
    "LLM_API_KEY": (str, "", True),
    "TOP_K": (int, 5, False),
    "RERANK": (bool, True, False),
    "MAX_LATENCY_S": (float, 10.0, False),
    "ALLOWED_ORIGINS": (list, [], False),
}


def parse_env_file(text):
    """KEY=VALUE per line. Skip blank lines and lines starting with #. Allow a leading "export ".
    Strip spaces around key and value, and one pair of matching quotes around the value ('x' or "x").
    Lines without "=" are ignored."""
    # TODO
    ...


def coerce(value, kind):
    """str -> as is; int/float -> int(value)/float(value); bool -> True for 1/true/yes/on, False for 0/false/no/off
    (case-insensitive), else ValueError; list -> comma-separated, items stripped, empty items dropped."""
    # TODO
    ...


def load_settings(environ, env_text="", fields=FIELDS):
    """For each field: the real environment wins, then the .env text, then the default.
    Collect problems for ALL fields before failing: "DATABASE_URL is required", "TOP_K: invalid int 'five'".
    Raise ValueError("; ".join(problems)) if any. Return {name: typed value}."""
    # TODO
    ...


def redacted(settings, fields=FIELDS):
    """A copy safe to log: secret values become "***" plus their last 4 characters if longer than 8 chars
    ("***f00d"), else "***". Empty secrets stay "". Non-secrets unchanged."""
    # TODO
    ...


if __name__ == "__main__":
    env_text = Path(".env").read_text(encoding="utf-8") if Path(".env").exists() else ""
    try:
        s = load_settings(os.environ, env_text)
        print(redacted(s))
    except ValueError as e:
        print("Configuration errors:", e)
        print("Create a .env file next to this one, e.g.:\nDATABASE_URL=postgresql://postgres:bench@localhost:5432/rag")
