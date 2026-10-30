"""Before you send the repository link to anyone: is everything there, and is nothing there
that shouldn't be?

A leaked API key in a public repository is found by bots within minutes. So this script
runs before every release push.

1. `REQUIRED`, `MUST_IGNORE`, `SECRET_PATTERNS`: what a release needs, what git must
   ignore, and what a secret looks like.
2. `missing_files`: required files that aren't there.
3. `ignored`: does `.gitignore` cover a name?
4. `find_secrets`: secret-looking lines in a text.
5. `scan` and `release_ok`: the whole repository, and the verdict.
"""
import fnmatch
import os
import re
from pathlib import Path

REQUIRED = ["README.md", "requirements.txt", "Dockerfile", "docker-compose.yml", ".env.example", ".gitignore", ".github/workflows/ci.yml"]
MUST_IGNORE = [".env", "feedback.db", "__pycache__/", "*.log"]
SECRET_PATTERNS = [
    ("anthropic_key", re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}")),
    ("openai_key", re.compile(r"sk-(?!ant-)[A-Za-z0-9_-]{20,}")),
    ("aws_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("password", re.compile(r"(?i)(password|passwd|pwd)\w*\s*[:=]\s*[\"'][^\"'\s$]{6,}[\"']")),   # a quoted literal
]
TEXT_EXT = {".py", ".md", ".yml", ".yaml", ".json", ".txt", ".toml", ".cfg", ".ini", ".html", ".js", ".env", ".example", ".sh", ".bat"}
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache"}
MAX_BYTES = 5_000_000


def missing_files(root, required=REQUIRED):
    """The required paths (relative to `root`) that don't exist, in order.

    A repository without a README or `.env.example` makes a bad first
    impression; without the CI file, there's no green badge.

    Example:
        >>> import tempfile
        >>> root = Path(tempfile.mkdtemp())
        >>> _ = (root / "README.md").write_text("# Dar Assistant")
        >>> missing_files(root, ["README.md", ".env.example", ".github/workflows/ci.yml"])
        ['.env.example', '.github/workflows/ci.yml']
    """
    return [p for p in required if not (Path(root) / p).exists()]


def ignored(name, gitignore_text):
    """True if a line of `.gitignore` covers `name`.

    A line covers it when it's equal, or when it's a wildcard pattern that
    matches (`fnmatch`: `*.log` matches `app.log`, `.env*` matches `.env`).
    Comments are skipped; a trailing `/` (a directory) is ignored on both sides.

    Example:
        >>> gi = "# local\\n.env*\\n*.log\\n__pycache__/\\n"
        >>> ignored(".env", gi), ignored("app.log", gi), ignored("__pycache__/", gi), ignored("feedback.db", gi)
        (True, True, True, False)
    """
    for line in gitignore_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        pat, target = line.rstrip("/"), name.rstrip("/")
        if pat == target or fnmatch.fnmatch(target, pat):
            return True
    return False


def find_secrets(text):
    """`[(kind, line number), ...]` for every secret-looking line.

    The patterns match the **shape** of real keys (`sk-ant-` plus 20+
    characters, `AKIA` plus 16...). The password rule only fires on a
    quoted literal of 6+ characters, so `${POSTGRES_PASSWORD:-bench}`,
    `os.environ[...]` and empty values are fine.

    Example:
        >>> key = "sk-ant-api03-" + "a1B2" * 6
        >>> find_secrets(f"x = 1\\nKEY = '{key}'\\npassword = 'hunter22'")
        [('anthropic_key', 2), ('password', 3)]
        >>> find_secrets("POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-bench}\\nLLM_API_KEY=\\npassword = os.environ['DB_PASSWORD']")
        []
    """
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        for kind, pat in SECRET_PATTERNS:
            if pat.search(line):
                out.append((kind, i))
    return out


def scan(root):
    """The full report for a repository folder.

    `os.walk` visits every folder; assigning `dirnames[:]` removes `.git`,
    virtualenvs and caches from the walk (huge, and not your code). Each
    file is checked for size (over 5 MB doesn't belong in git) and, if it's
    text, for secrets.

    Example:
        >>> import tempfile
        >>> root = Path(tempfile.mkdtemp())
        >>> _ = (root / ".gitignore").write_text(".env\\n__pycache__/\\n")
        >>> _ = (root / "llm.py").write_text("client = Client(api_key='" + "sk-ant-api03-" + "a1B2" * 6 + "')")
        >>> r = scan(root)
        >>> r["not_ignored"], r["secrets"]
        (['feedback.db', '*.log'], [('llm.py', 'anthropic_key', 1)])
    """
    root = Path(root)
    gi = (root / ".gitignore").read_text(encoding="utf-8") if (root / ".gitignore").exists() else ""
    secrets, large = [], []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            p = Path(dirpath) / f
            rel = p.relative_to(root).as_posix()
            if p.stat().st_size > MAX_BYTES:
                large.append(rel)
                continue
            if p.suffix in TEXT_EXT or f == ".env":
                for kind, line in find_secrets(p.read_text(encoding="utf-8", errors="replace")):
                    secrets.append((rel, kind, line))
    return {"missing": missing_files(root), "not_ignored": [n for n in MUST_IGNORE if not ignored(n, gi)],
            "secrets": sorted(secrets), "large": sorted(large)}


def release_ok(report, allow_secret_paths=(".env",)):
    """The verdict: nothing missing, everything ignored, no large files, and
    secrets **only** in your local `.env` (which `.gitignore` keeps out of git).

    Example:
        >>> release_ok({"missing": [], "not_ignored": [], "large": [], "secrets": [(".env", "anthropic_key", 1)]})
        True
        >>> release_ok({"missing": [], "not_ignored": [], "large": [], "secrets": [("app/llm.py", "anthropic_key", 3)]})
        False
    """
    return (not report["missing"] and not report["not_ignored"] and not report["large"]
            and all(path in allow_secret_paths for path, _, _ in report["secrets"]))


def print_report(r):
    """One line per kind of problem, then the verdict.

    Example:
        >>> print_report({"missing": [], "not_ignored": [], "secrets": [], "large": []})
        missing      ok
        not_ignored  ok
        secrets      ok
        large        ok
        READY TO SHARE
    """
    for k, v in r.items():
        print(f"{k:12}", v or "ok")
    print("READY TO SHARE" if release_ok(r) else "NOT READY: fix the items above")


if __name__ == "__main__":
    import sys
    import tempfile
    if len(sys.argv) > 1:
        r = scan(sys.argv[1])               # python release_check.py path/to/your/project
        print_report(r)
        sys.exit(0 if release_ok(r) else 1)
    # Demo: a project folder with two classic mistakes, then the same folder fixed.
    root = Path(tempfile.mkdtemp())
    key = "sk-ant-api03-" + "Xy7Q" * 6
    files = {"README.md": "# Dar Assistant", "requirements.txt": "fastapi\n", "Dockerfile": "FROM python:3.12-slim\n",
             "docker-compose.yml": "services: {}\n", ".gitignore": ".env\n__pycache__/\n",
             ".env": f"LLM_API_KEY={key}\n", "app/llm.py": f"API_KEY = '{key}'   # just for testing\n"}
    for name, content in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(content, encoding="utf-8")
    print("--- before")
    print_report(scan(root))
    (root / "app/llm.py").write_text("import os\nAPI_KEY = os.environ['LLM_API_KEY']\n", encoding="utf-8")
    (root / ".gitignore").write_text(".env\nfeedback.db\n__pycache__/\n*.log\n", encoding="utf-8")
    (root / ".env.example").write_text("LLM_API_KEY=\n", encoding="utf-8")
    (root / ".github/workflows").mkdir(parents=True)
    (root / ".github/workflows/ci.yml").write_text("name: CI\n", encoding="utf-8")
    print("\n--- after the fixes")
    print_report(scan(root))
