import tempfile
from pathlib import Path
mf = fn("missing_files")
def repo(files):
    root = Path(tempfile.mkdtemp())
    for name, content in files.items():
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content) if isinstance(content, bytes) else p.write_text(content, encoding="utf-8")
    return root
check("missing_files in order", lambda: mf(repo({"README.md": "x", "Dockerfile": "x"}), ["README.md", ".env.example", "Dockerfile", ".github/workflows/ci.yml"]) == [".env.example", ".github/workflows/ci.yml"])
ig = fn("ignored")
GI = "# local\n.env*\n*.log\n__pycache__/\n"
check("ignored: exact names, patterns, directories, comments skipped", lambda: ig(".env", GI) and ig("app.log", GI) and ig("__pycache__/", GI) and not ig("feedback.db", GI) and not ig("local", GI))
fs = fn("find_secrets")
key = "sk-ant-api03-" + "a1B2" * 6
check("find_secrets: API keys with their line", lambda: fs(f"x = 1\nKEY = '{key}'\n") == [("anthropic_key", 2)] and fs("OPENAI=sk-" + "Z9y8" * 6) == [("openai_key", 1)])
check("find_secrets: passwords, AWS keys, private keys", lambda: [k for k, _ in fs("password = 'hunter22'\nAKIA" + "ABCD1234EFGH5678" + "\n-----BEGIN RSA PRIVATE KEY-----")] == ["password", "aws_key", "private_key"])
check("find_secrets: placeholders and env references are fine", lambda: fs("POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-bench}\nLLM_API_KEY=\npassword = os.environ['DB_PASSWORD']\nsk-ant-xxx") == [])
sc = fn("scan")
def full(extra=None):
    files = {"README.md": "# Project", "requirements.txt": "fastapi", "Dockerfile": "FROM python:3.12-slim", "docker-compose.yml": "services: {}",
             ".env.example": "LLM_API_KEY=\n", ".gitignore": ".env\nfeedback.db\n__pycache__/\n*.log\n", ".github/workflows/ci.yml": "name: CI",
             "app/main.py": "print('hi')", ".env": f"LLM_API_KEY={key}\n", ".git/config": f"token {key}"}
    files.update(extra or {})
    return repo(files)
check("scan: a clean repo has nothing to report except the local .env", lambda: sc(full()) == {"missing": [], "not_ignored": [], "secrets": [(".env", "anthropic_key", 1)], "large": []})
check("scan finds a key in code and skips .git", lambda: sc(full({"app/llm.py": f"\n\nclient = Client(api_key='{key}')"}))["secrets"] == [(".env", "anthropic_key", 1), ("app/llm.py", "anthropic_key", 3)])
check("scan flags large files and gitignore gaps", lambda: (lambda r: r["large"] == ["data/dump.bin"] and r["not_ignored"] == ["feedback.db", "*.log"])(sc(full({"data/dump.bin": b"0" * 5_000_001, ".gitignore": ".env\n__pycache__/\n"}))))
ro = fn("release_ok")
check("release_ok: only the local .env may hold secrets", lambda: ro(sc(full())) and not ro(sc(full({"app/llm.py": f"k='{key}'"}))) and not ro({"missing": ["Dockerfile"], "not_ignored": [], "secrets": [], "large": []}))
