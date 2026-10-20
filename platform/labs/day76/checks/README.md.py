import re
clean = re.sub(r"<!--.*?-->", "", src, flags=re.S)
sections = {m.group(1).strip().lower(): m.group(2) for m in re.finditer(r"^## ([^\n]+)\n(.*?)(?=^## |\Z)", clean, re.M | re.S)}
body = lambda name: sections.get(name, "").strip()
need = ["what it does", "architecture", "quickstart", "configuration", "evaluation", "limitations"]
check("all six sections are present", lambda: all(n in sections for n in need))
check("no TODO comments left", "TODO" not in src)
check("a real title (not 'Project name') and a one-line description", lambda: (lambda m: m and m.group(1).strip() != "Project name")(re.match(r"# (.+)\n", clean)) and len(clean.split("##")[0].split("\n", 1)[1].strip()) >= 30)
check("a CI badge", lambda: re.search(r"!\[[^\]]*\]\(https://github\.com/[^)]+/actions/workflows/[^)]+badge\.svg\)", clean))
check("Architecture has a Mermaid diagram", lambda: re.search(r"```mermaid\n\s*(flowchart|graph)\s", body("architecture")))
check("Quickstart: a code block with docker compose up", lambda: re.search(r"```(bash|sh|shell|powershell|console)?\n.*docker compose up.*```", body("quickstart"), re.S))
check("Quickstart copies .env.example (no secrets in the repo)", lambda: ".env.example" in body("quickstart"))
rows = lambda: [l for l in body("configuration").splitlines() if re.match(r"\s*\|\s*`?[A-Z][A-Z0-9_]+`?\s*\|", l)]
check("Configuration table with at least 4 variables", lambda: len(rows()) >= 4)
check("Evaluation: numbers with intervals and the test set size", lambda: re.search(r"\d?\.\d+\s*\[\s*\d?\.\d+\s*,\s*\d?\.\d+\s*\]", body("evaluation")) and re.search(r"\d+\s+(test\s+)?questions", body("evaluation"), re.I))
check("at least 2 limitations", lambda: len(re.findall(r"^\s*[-*]\s+\S", body("limitations"), re.M)) >= 2)
check("at least 250 words", lambda: len(clean.split()) >= 250)
