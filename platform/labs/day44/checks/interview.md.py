import re

sections = {m.group(1).strip().lower(): m.group(2) for m in re.finditer(r"^## ([^\n]+)\n(.*?)(?=^## |\Z)", src, re.M | re.S)}
body = lambda name: re.sub(r"<!--.*?-->", "", sections.get(name, ""), flags=re.S).strip()
bullets = lambda name: re.findall(r"^\s*(?:[-*]|\d+[.)])\s+\S", body(name), re.M)
need = ["user", "today's workflow", "pain points", "their questions", "documents and data", "success looks like", "constraints"]
check("all seven sections are present", lambda: all(n in sections for n in need))
check("no TODO comments left", "TODO" not in src)
check("every section has content", lambda: all(len(body(n)) >= 15 for n in need))
check("the workflow is a list of at least 3 steps", lambda: len(bullets("today's workflow")) >= 3)
check("at least 3 pain points, one with a number", lambda: len(bullets("pain points")) >= 3 and re.search(r"\d", body("pain points")))
check("at least 8 real questions", lambda: len(bullets("their questions")) >= 8)
check("questions look like questions (? or ؟ on most of them)", lambda: sum(1 for l in body("their questions").splitlines() if re.search(r"[?؟]", l)) >= 6)
check("documents: format and a rough count", lambda: re.search(r"\d", body("documents and data")) and re.search(r"pdf|scan|word|docx|whatsapp|excel|email|image|photo", body("documents and data"), re.I))
