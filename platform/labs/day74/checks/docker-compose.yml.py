import re
code = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
def block(name):
    m = re.search(rf"^  {name}:\s*\n((?:(?:    .*|\s*)\n)*)", code + "\n", re.M)
    return m.group(1) if m else ""
check("services db, ollama and api are defined", lambda: all(block(s).strip() for s in ("db", "ollama", "api")))
check("db: pgvector image and a named data volume", lambda: "pgvector/pgvector" in block("db") and re.search(r"-\s*\w+:/var/lib/postgresql/data", block("db")))
check("db: healthcheck with pg_isready", lambda: "healthcheck" in block("db") and "pg_isready" in block("db"))
check("ollama: a named volume for the models", lambda: re.search(r"-\s*\w+:/root/\.ollama", block("ollama")))
check("api: built from this folder, port 8000 published", lambda: re.search(r"build:\s*\.", block("api")) and re.search(r"[\"']?8000:8000", block("api")))
check("api: env_file for secrets", lambda: re.search(r"env_file:\s*(\.env|\n\s*-\s*\.env)", block("api")))
check("api: DATABASE_URL and OLLAMA_URL use service names, not localhost", lambda: re.search(r"DATABASE_URL[:=].*@db:5432", block("api")) and re.search(r"OLLAMA_URL[:=]\s*http://ollama:11434", block("api")) and not re.search(r"(DATABASE_URL|OLLAMA_URL)[:=].*localhost", block("api")))
check("api waits for a healthy db", lambda: re.search(r"depends_on:\s*\n\s+db:\s*\n\s+condition:\s*service_healthy", block("api")))
check("api: restart policy and a healthcheck on /health", lambda: re.search(r"restart:\s*(unless-stopped|always)", block("api")) and "healthcheck" in block("api") and "/health" in block("api"))
check("named volumes declared at the top level", lambda: re.search(r"^volumes:\s*\n(\s+\w+:\s*\n?)+", code, re.M))
check("no secrets written in the file", lambda: not re.search(r"(sk-[A-Za-z0-9]{8,}|API_KEY:\s*\S{6,})", code))
