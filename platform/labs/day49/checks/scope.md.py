import re

clean = re.sub(r"<!--.*?-->", "", src, flags=re.S)
sections = {m.group(1).strip().lower(): m.group(2) for m in re.finditer(r"^## ([^\n]+)\n(.*?)(?=^## |\Z)", clean, re.M | re.S)}
body = lambda name: sections.get(name, "").strip()
bullets = lambda name: re.findall(r"^\s*(?:[-*]|\d+[.)])\s+\S", body(name), re.M)
need = ["problem", "user", "in scope", "out of scope", "data", "success metrics", "timeline", "sign-off"]
check("all eight sections are present", lambda: all(n in sections for n in need))
check("no TODO comments left", "TODO" not in src)
check("every section has content", lambda: all(len(body(n)) >= 10 for n in need))
check("the problem has a number", lambda: re.search(r"\d", body("problem")))
check("at least 3 bullets in scope and 3 out of scope", lambda: len(bullets("in scope")) >= 3 and len(bullets("out of scope")) >= 3)
check("at least 3 success metrics, each with a number", lambda: len(bullets("success metrics")) >= 3 and all(re.search(r"\d", l) for l in body("success metrics").splitlines() if re.match(r"\s*[-*]", l)))
check("the timeline covers weeks 8 to 12", lambda: all(re.search(rf"\b{w}\b", body("timeline")) for w in range(8, 13)))
check("sign-off has a date", lambda: re.search(r"\d{4}-\d{2}-\d{2}|\d{1,2}[/.]\d{1,2}[/.]\d{2,4}|\b(nov|dec)\w*\b", body("sign-off"), re.I))
check("fits on one page (under 600 words)", lambda: len(clean.split()) < 600)
