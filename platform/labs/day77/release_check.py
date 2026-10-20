# Before you send the repository link to anyone: is everything there, and is nothing there that shouldn't be?
# A leaked API key in a public repo gets found by bots within minutes. Check before every push of a release.
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
    """Required paths (relative to root) that don't exist, in the given order."""
    # TODO
    ...


def ignored(name, gitignore_text):
    """True if a non-comment line of .gitignore matches name: equal to it, or an fnmatch pattern matching it
    (".env*" matches ".env"; "*.log" matches "app.log"). Trailing "/" on both sides is ignored for directories."""
    # TODO
    ...


def find_secrets(text):
    """[(kind, line number from 1), ...] for every SECRET_PATTERNS match, line by line, in pattern order per line."""
    # TODO
    ...


def scan(root):
    """{"missing": missing_files, "not_ignored": MUST_IGNORE entries not covered by .gitignore,
    "secrets": [(relative path with "/", kind, line)], "large": [relative paths over MAX_BYTES]}.
    Walk all files except SKIP_DIRS; search secrets in files whose suffix (or name, for ".env") is in TEXT_EXT.
    Sorted by path."""
    # TODO
    ...


def release_ok(report, allow_secret_paths=(".env",)):
    """True when nothing is missing, everything is ignored, no large files, and every secret found is in a file
    listed in allow_secret_paths (your local .env, which .gitignore keeps out of git)."""
    # TODO
    ...


if __name__ == "__main__":
    import sys
    r = scan(sys.argv[1] if len(sys.argv) > 1 else "..")
    for k, v in r.items():
        print(f"{k:12}", v or "ok")
    print("READY TO SHARE" if release_ok(r) else "NOT READY: fix the items above")
    sys.exit(0 if release_ok(r) else 1)
