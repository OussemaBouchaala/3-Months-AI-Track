import re
clean = re.sub(r"<!--.*?-->", "", src, flags=re.S)
sections = {m.group(1).strip().lower(): m.group(2) for m in re.finditer(r"^## ([^\n]+)\n(.*?)(?=^## |\Z)", clean, re.M | re.S)}
body = lambda name: sections.get(name, "").strip()
bullets = lambda name: re.findall(r"^\s*(?:[-*]|\d+[.)])\s+\S", body(name), re.M)
need = ["participants", "tasks", "results", "issues", "changes made", "next"]
check("all six sections are present", lambda: all(n in sections for n in need))
check("no TODO comments left", "TODO" not in src)
check("every section has content", lambda: all(len(body(n)) >= 15 for n in need))
check("participants: a count between 3 and 5", lambda: any(3 <= int(n) <= 5 for n in re.findall(r"\b\d\b", body("participants"))) or re.search(r"\b(three|four|five|trois|quatre|cinq)\b", body("participants"), re.I))
check("at least 2 numbered tasks", lambda: len(re.findall(r"^\s*\d+[.)]\s", body("tasks"), re.M)) >= 2)
check("results: a task table and a SUS score", lambda: body("results").count("|") >= 10 and re.search(r"SUS[^\n]*\d", body("results"), re.I))
check("at least 3 issues, each tagged with a severity", lambda: len(bullets("issues")) >= 3 and all(re.search(r"\[(high|medium|low)\]", l, re.I) for l in body("issues").splitlines() if re.match(r"\s*(?:[-*]|\d+[.)])\s", l)))
check("at least 2 changes made", lambda: len(bullets("changes made")) >= 2)
