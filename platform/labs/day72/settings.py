"""Hard-coded "localhost:5432" and an API key in the code work on your laptop and nowhere else.

One settings module instead (the "config" rule of twelve-factor apps): typed values from
the environment, a `.env` file for local development, defaults, **all** missing values
reported at once, and secrets never printed.

1. `FIELDS`: every setting with its type, default, and whether it's secret.
2. `parse_env_file`: read a `.env` file.
3. `coerce`: text -> int, float, bool or list.
4. `load_settings`: environment > .env > default, with every problem in one error.
5. `redacted`: a copy that's safe to log.
"""
import os
from pathlib import Path

REQUIRED = object()          # a unique marker: "no default, must be set"
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
    """Read `KEY=VALUE` lines into a dict of strings.

    - Skip blank lines, `#` comments, and lines without `=`.
    - Accept a leading `export ` (so the same file works with `source .env`).
    - `partition("=")` splits at the **first** `=` only, so `URL=a=b` keeps `a=b`.
    - Remove one pair of matching quotes: `'x'` or `"x"`.

    Example:
        >>> parse_env_file('# local dev\\nexport DATABASE_URL = "postgresql://u:p@db:5432/rag"\\nTOP_K=8\\nbroken line\\nURL=a=b')
        {'DATABASE_URL': 'postgresql://u:p@db:5432/rag', 'TOP_K': '8', 'URL': 'a=b'}
    """
    out = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[7:]
        key, _, value = line.partition("=")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]
        out[key.strip()] = value
    return out


def coerce(value, kind):
    """Turn the text of an environment variable into the right type.

    - `int` / `float` / `str`: call the type.
    - `bool`: strict. Only 1/true/yes/on and 0/false/no/off (any case).
      `bool("false")` would be `True` in Python, a classic bug.
    - `list`: comma-separated, items trimmed, empty items dropped.

    Example:
        >>> coerce("8", int), coerce("2.5", float), coerce("OFF", bool)
        (8, 2.5, False)
        >>> coerce(" http://a , http://b,, ", list)
        ['http://a', 'http://b']
        >>> coerce("maybe", bool)
        Traceback (most recent call last):
        ValueError: not a boolean: 'maybe'
    """
    if kind is bool:
        v = value.strip().lower()
        if v in ("1", "true", "yes", "on"):
            return True
        if v in ("0", "false", "no", "off"):
            return False
        raise ValueError(f"not a boolean: {value!r}")
    if kind is list:
        return [x.strip() for x in value.split(",") if x.strip()]
    return kind(value)


def load_settings(environ, env_text="", fields=FIELDS):
    """The final settings, typed.

    For each field: the **real environment** wins (Docker and CI set it),
    then the `.env` text (your laptop), then the default.

    Problems are **collected** for all fields before failing: one run tells
    you everything that's wrong, instead of fixing one variable per restart.

    Example:
        >>> s = load_settings({"TOP_K": "3"}, "DATABASE_URL=postgresql://u:p@db/rag\\nTOP_K=8")
        >>> s["TOP_K"], s["RERANK"], s["DATABASE_URL"]
        (3, True, 'postgresql://u:p@db/rag')
        >>> try:
        ...     load_settings({"TOP_K": "five", "RERANK": "maybe"}, "")
        ... except ValueError as e:
        ...     print(e)
        DATABASE_URL is required; TOP_K: invalid int 'five'; RERANK: invalid bool 'maybe'
    """
    file_vals = parse_env_file(env_text)
    out, problems = {}, []
    for name, (kind, default, _secret) in fields.items():
        raw = environ.get(name, file_vals.get(name))
        if raw is None:
            if default is REQUIRED:
                problems.append(f"{name} is required")
            else:
                out[name] = default
            continue
        try:
            out[name] = coerce(raw, kind)
        except ValueError:
            problems.append(f"{name}: invalid {kind.__name__} {raw!r}")
    if problems:
        raise ValueError("; ".join(problems))
    return out


def redacted(settings, fields=FIELDS):
    """A copy of the settings that's safe to print or log.

    Secrets become `***` plus their last 4 characters when long enough:
    enough to tell which key is loaded, not enough to use it. Short secrets
    become just `***`; an empty one stays empty (so you see it's missing).

    Example:
        >>> redacted({"DATABASE_URL": "postgresql://u:secret@db:5432/rag", "LLM_API_KEY": "short", "TOP_K": 5})
        {'DATABASE_URL': '***/rag', 'LLM_API_KEY': '***', 'TOP_K': 5}
    """
    out = {}
    for name, value in settings.items():
        secret = fields.get(name, (None, None, False))[2]
        if secret and value:
            out[name] = "***" + value[-4:] if len(value) > 8 else "***"
        else:
            out[name] = value
    return out


if __name__ == "__main__":
    env_text = Path(".env").read_text(encoding="utf-8") if Path(".env").exists() else ""
    try:
        s = load_settings(os.environ, env_text)
        print("your settings:", redacted(s))
    except ValueError as e:
        print("Your configuration errors:", e)
        print("Create a .env file next to this one, e.g.:\nDATABASE_URL=postgresql://postgres:bench@localhost:5432/rag\n")
        demo = "DATABASE_URL=postgresql://postgres:bench@localhost:5432/rag\nLLM_API_KEY=sk-demo-1234abcd\nRERANK=no\n"
        print("With that .env plus TOP_K=3 in the environment:")
        print(redacted(load_settings({"TOP_K": "3"}, demo)))
