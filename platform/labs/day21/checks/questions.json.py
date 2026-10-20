import json
import re

try:
    items = json.loads(src)
    parse_error = None
except Exception as exc:
    items, parse_error = [], exc
check("questions.json is valid JSON", parse_error is None, f"{parse_error}" if parse_error else "")
check("at least 20 questions", len(items) >= 20, f"You have {len(items)}.")
check("each item has question, lang, answer, source_ids",
      lambda: all({"question", "lang", "answer", "source_ids"} <= set(i) for i in items))
valid_ids = {f"c{n}" for n in range(14)}
check("source_ids are chunk ids c0..c13", lambda: all(set(i["source_ids"]) <= valid_ids for i in items),
      "Open ../day15/chunks.json to see the ids.")
by_lang = lambda l: [i for i in items if i.get("lang") == l]
check("at least 4 questions in each of en, fr, ar", lambda: all(len(by_lang(l)) >= 4 for l in ("en", "fr", "ar")))
check("Arabic questions are written in Arabic script", lambda: by_lang("ar") and all(re.search(r"[؀-ۿ]", i["question"]) for i in by_lang("ar")))
check("at least 2 unanswerable questions (no sources, empty answer)",
      lambda: sum(1 for i in items if not i["source_ids"] and not i["answer"].strip()) >= 2)
check("answerable questions have an expected answer", lambda: all(i["answer"].strip() for i in items if i["source_ids"]))
check("no duplicate questions", lambda: len({i["question"].strip().lower() for i in items}) == len(items))
