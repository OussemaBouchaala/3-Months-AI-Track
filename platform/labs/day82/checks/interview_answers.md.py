import re
clean = re.sub(r"<!--.*?-->", "", src, flags=re.S)
secs = {m.group(1).strip(): m.group(2).strip() for m in re.finditer(r"^## ([^\n]+)\n(.*?)(?=^## |\Z)", clean, re.M | re.S)}
answers = {k: v for k, v in secs.items() if re.match(r"Q\d+:", k)}
words = lambda t: len(t.split())
def ans(pattern):
    for k, v in answers.items():
        if re.search(pattern, k, re.I):
            return v
    return ""
check("no TODO comments left", "TODO" not in src)
check("the five questions are answered", lambda: len(answers) >= 5 and all(ans(p) for p in [r"proud|project", r"hardest|difficult|challeng", r"evaluat|know .*work", r"fail|mistake", r"why|design|alternative"]))
check("each answer is 80-250 words (30-90 seconds spoken)", lambda: all(80 <= words(v) <= 250 for v in answers.values()) or (_ for _ in ()).throw(CheckFailed(", ".join(f"{k[:3]} has {words(v)} words" for k, v in answers.items() if not 80 <= words(v) <= 250))))
check("each answer has at least one number", lambda: all(re.search(r"\d", v) for v in answers.values()))
check("first person: what YOU did", lambda: all(len(re.findall(r"\bI\b", v)) >= 2 for v in answers.values()))
check("the failure answer says what you learned", lambda: re.search(r"\blearn(ed|t)?\b|lesson|now I|since then", ans(r"fail|mistake"), re.I))
check("the evaluation answer mentions a held-out/test set and a metric", lambda: re.search(r"test set|held.out|golden", ans(r"evaluat|know .*work"), re.I) and re.search(r"accura|recall|correct|precision|kappa|interval", ans(r"evaluat|know .*work"), re.I))
check("the design answer names the alternative and the trade-off", lambda: re.search(r"instead of|rather than|alternative|vs\.?|versus", ans(r"why|design|alternative"), re.I) and re.search(r"trade.?off|cost|but|downside|price", ans(r"why|design|alternative"), re.I))
qs = lambda: secs.get("Questions I'll ask them", "")
check("at least 3 questions for them", lambda: len([l for l in qs().splitlines() if l.strip().endswith("?")]) >= 3)
