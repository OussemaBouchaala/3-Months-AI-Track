import re

clean = re.sub(r"<!--.*?-->", "", src, flags=re.S)
sections = {m.group(1).strip().lower(): m.group(2) for m in re.finditer(r"^## ([^\n]+)\n(.*?)(?=^## |\Z)", clean, re.M | re.S)}
body = lambda name: sections.get(name, "").strip()
bullets = lambda name: re.findall(r"^\s*(?:[-*]|\d+[.)])\s+\S", body(name), re.M)
need = ["overview", "components", "diagram", "data flow", "storage", "decisions", "risks"]
check("all seven sections are present", lambda: all(n in sections for n in need))
check("no TODO comments left", "TODO" not in src)
check("every section has content", lambda: all(len(body(n)) >= 20 for n in need))
merm = lambda: re.search(r"```mermaid\n(.*?)```", body("diagram"), re.S)
check("Diagram has a mermaid block (outside comments)", lambda: merm() is not None and re.match(r"\s*(flowchart|graph)\s+(LR|TD|TB|RL)", merm().group(1)))
check("the diagram has at least 5 arrows", lambda: len(re.findall(r"-->|-\.->|==>", merm().group(1))) >= 5)
check("at least 5 components", lambda: len(bullets("components")) >= 5)
check("data flow has at least 4 numbered steps", lambda: len(re.findall(r"^\s*\d+[.)]\s", body("data flow"), re.M)) >= 4)
check("decisions say 'instead of' and 'because'", lambda: len(bullets("decisions")) >= 2 and "instead of" in body("decisions").lower() and "because" in body("decisions").lower())
check("at least 2 risks", lambda: len(bullets("risks")) >= 2)
