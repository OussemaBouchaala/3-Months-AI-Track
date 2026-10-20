import re

sections = {m.group(1).strip().lower(): m.group(2) for m in re.finditer(r"^## ([^\n]+)\n(.*?)(?=^## |\Z)", src, re.M | re.S)}
body = lambda name: re.sub(r"<!--.*?-->", "", sections.get(name, ""), flags=re.S).strip()
need = ["summary", "corpus", "pipeline", "results", "what worked", "what didn't", "next"]
check("all seven sections are present", lambda: all(n in sections for n in need))
check("no TODO comments left", "TODO" not in src)
check("every section has content", lambda: all(len(body(n)) >= 20 for n in need))
rows = lambda: [l for l in body("results").splitlines() if l.strip().startswith("|") and not re.match(r"^\s*\|[\s|:-]+\|\s*$", l)]
check("Results has a Markdown table with a header and at least 2 configurations", lambda: len(rows()) >= 3)
check("the table holds real numbers (decimals or %)", lambda: len(re.findall(r"\d+(?:\.\d+)?\s*%|0\.\d+|1\.0", body("results"))) >= 4)
check("Corpus gives the document and question counts", lambda: len(re.findall(r"\d+", body("corpus"))) >= 2)
check("Pipeline lists at least 4 stages", lambda: len(re.findall(r"^\s*[-*\d]", body("pipeline"), re.M)) >= 4)
check("What worked and What didn't have 2 bullets each", lambda: all(len(re.findall(r"^\s*[-*\d]", body(n), re.M)) >= 2 for n in ("what worked", "what didn't")))
check("at least 200 words", lambda: len(re.sub(r"<!--.*?-->", "", src, flags=re.S).split()) >= 200)
