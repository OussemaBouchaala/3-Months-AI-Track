import re

code = "\n".join(l.split("#")[0] for l in src.splitlines())
check("uses the pgvector image", re.search(r"image:\s*['\"]?pgvector/pgvector", code) is not None,
      "image: pgvector/pgvector:pg17")
check("publishes port 5432", re.search(r"['\"]?\d+:5432['\"]?", code) is not None, '- "5432:5432"')
check("mounts a named volume on the data folder", re.search(r"-\s*pgdata:/var/lib/postgresql/data", code) is not None,
      "- pgdata:/var/lib/postgresql/data")
check("no TODO placeholders left", "..." not in code)
check("sets a password", re.search(r"POSTGRES_PASSWORD:\s*\S+", code) is not None)
