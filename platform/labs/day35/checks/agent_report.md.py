import re

sections = {m.group(1).strip().lower(): m.group(2) for m in re.finditer(r"^## ([^\n]+)\n(.*?)(?=^## |\Z)", src, re.M | re.S)}
body = lambda name: re.sub(r"<!--.*?-->", "", sections.get(name, ""), flags=re.S).strip()
need = ["what the agent does", "tools", "results", "failures", "guardrails", "next"]
check("all six sections are present", lambda: all(n in sections for n in need))
check("no TODO comments left", "TODO" not in src)
check("every section has content", lambda: all(len(body(n)) >= 20 for n in need))
check("Results give a success rate in % and the number of scenarios", lambda: re.search(r"\d+\s*%", body("results")) and re.search(r"\d+\s*/\s*\d+|\d+\s+scenarios", body("results")))
check("Failures describe at least 2 cases", lambda: len(re.findall(r"^\s*[-*\d]", body("failures"), re.M)) >= 2)
check("Tools lists at least 2 tools", lambda: len(re.findall(r"^\s*[-*]", body("tools"), re.M)) >= 2)
check("Guardrails mention confirmation and idempotency", lambda: "confirm" in body("guardrails").lower() and "idempot" in body("guardrails").lower())
check("at least 150 words", lambda: len(re.sub(r"<!--.*?-->", "", src, flags=re.S).split()) >= 150)
