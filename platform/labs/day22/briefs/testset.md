# 50 questions you trust
**Topic:** a model drafts, a human decides: validated, deduplicated, reviewed test items.

## Real example
A language school wants 100 quiz questions. A model drafts them from the lessons, code throws away malformed and duplicate ones, and a teacher reviews what's left. The model is faked here:

```python
import json, re

FENCE = "`" * 3   # models love wrapping JSON in a fenced block
fake_reply = ("Sure! Here you go:\n" + FENCE + "json\n"
              '[{"question": "What does bonjour mean?", "answer": "hello"}, '
              '{"question": "What does BONJOUR mean??", "answer": "hello"}, {"question": "Merci = ?", "answer": "thanks"}]\n' + FENCE)
raw = fake_reply[fake_reply.find("["): fake_reply.rfind("]") + 1]
drafts = json.loads(raw)

seen, kept = set(), []
for d in drafts:
    key = re.sub(r"[^\w\s]", "", d["question"].lower()).strip()
    if key not in seen:
        seen.add(key); kept.append(d)
print(len(drafts), "drafted ->", len(kept), "kept:", [k["question"] for k in kept])
```

## Your mission
Validate your 20 questions, draft ~40 candidates with a model, review, and freeze 50.

## Steps
1. `TestItem`: four fields; `lang` is `Literal["en", "fr", "ar"]`.
2. `kind`, `load_testset`, `summary` (use `Counter`).
3. `generation_prompt` and `parse_generated` (cut from the first `[` to the last `]`, skip bad items).
4. `dedupe` on normalized questions.
5. **Run**, open `candidates.json`, delete weak ones, fix wording, save 50 items as `testset_v1.json`.

## Done when
**Check** passes and `testset_v1.json` holds 50 reviewed questions.
