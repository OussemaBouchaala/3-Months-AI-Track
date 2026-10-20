import re
clean = re.sub(r"<!--.*?-->", "", src, flags=re.S)
sections = {m.group(1).strip().lower(): m.group(2) for m in re.finditer(r"^## ([^\n]+)\n(.*?)(?=^## |\Z)", clean, re.M | re.S)}
body = lambda name: sections.get(name, "").strip()
bullets = lambda name: re.findall(r"^\s*(?:[-*]|\d+[.)])\s+\S", body(name), re.M)
need = ["setup", "results", "recommendation", "failures", "cost", "limitations"]
check("all six sections are present", lambda: all(n in sections for n in need))
check("no TODO comments left", "TODO" not in src)
check("every section has content", lambda: all(len(body(n)) >= 20 for n in need))
check("setup gives the test set size", lambda: re.search(r"\d+\s*(questions|items|questions?)", body("setup"), re.I))
rows = lambda: [l for l in body("results").splitlines() if l.strip().startswith("|") and not re.match(r"^\s*\|[\s|:-]+\|\s*$", l)]
check("results table: header and at least 2 configurations", lambda: len(rows()) >= 3)
check("results carry confidence intervals like 0.84 [0.74, 0.92]", lambda: len(re.findall(r"\d?\.\d+\s*\[\s*\d?\.\d+\s*,\s*\d?\.\d+\s*\]", body("results"))) >= 2)
check("the recommendation names a config from the table", lambda: any(r.split("|")[1].strip() and r.split("|")[1].strip() in body("recommendation") for r in rows()[1:]))
check("failures: at least 3 categories with counts", lambda: len([l for l in body("failures").splitlines() if re.match(r"\s*(?:[-*]|\d+[.)])\s", l) and re.search(r"\d", l)]) >= 3)
check("cost gives a monthly figure", lambda: re.search(r"\d", body("cost")) and re.search(r"month|mois", body("cost"), re.I))
check("at least 2 limitations", lambda: len(bullets("limitations")) >= 2)
