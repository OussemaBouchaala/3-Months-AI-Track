import re

text = re.sub(r"<!--.*?-->", "", src, flags=re.S)
sections = dict(re.findall(r"^## (.+?)\n(.*?)(?=^## |\Z)", text, flags=re.M | re.S))
for name in ["Problem", "Architecture", "Results", "Run it", "What I'd improve"]:
    check(f"'{name}' section is written", lambda name=name: len(sections.get(name, "").strip()) >= 30,
          "Replace the TODO comment with real content.")
check("Results contains a Markdown table", lambda: "|---" in sections.get("Results", "") or "| ---" in sections.get("Results", ""),
      "Paste the table from day12/results.md.")
check("Improvements are a list of at least 3 points",
      lambda: len(re.findall(r"^\s*[-*] ", sections.get("What I'd improve", ""), flags=re.M)) >= 3)
