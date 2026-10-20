import re

code = "\n".join(l for l in src.splitlines() if not l.strip().startswith("#"))
check("Has an api service built from this folder", re.search(r"^\s+api:\s*$", code, re.M) and re.search(r"build:\s*\.", code))
check("Publishes port 8002", "8002:8002" in code)
check("api reaches Ollama by service name: http://ollama:11434", "http://ollama:11434" in code,
      "OLLAMA_URL: http://ollama:11434  (each container has its own localhost)")
check("Has an ollama service using the ollama/ollama image", re.search(r"image:\s*ollama/ollama", code) is not None)
check("Models persist in a named volume at /root/.ollama", re.search(r"-?\s*\w[\w-]*:/root/\.ollama", code) is not None
      and re.search(r"^volumes:\s*$", code, re.M) is not None,
      "In ollama: `volumes: [ollama:/root/.ollama]`, plus a top-level `volumes:` with `ollama:` under it.")
check("api starts after ollama (depends_on)", "depends_on" in code)
