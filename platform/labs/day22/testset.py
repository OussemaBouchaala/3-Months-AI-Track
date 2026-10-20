# Grow the test set from 20 to 50 questions: validate it, let a model draft candidates, YOU review them.
# Check needs no model. Run drafts candidates with your ⚙ AI model into candidates.json.
import json
import re
from typing import Literal

from pydantic import BaseModel, ValidationError

KINDS = ("single", "multi", "unanswerable")


class TestItem(BaseModel):
    # TODO: question: str, lang: Literal["en", "fr", "ar"], answer: str, source_ids: list[str]
    ...


def kind(item):
    """'unanswerable' when source_ids is empty, 'multi' when 2+ sources, else 'single'."""
    # TODO
    ...


def load_testset(path):
    """Read a JSON list and validate every element with TestItem.model_validate.
    Return a list of TestItem. Let ValidationError propagate: a broken test set must stop you."""
    # TODO
    ...


def summary(items):
    """Count items by lang and by kind: {"lang": {"en": 7, ...}, "kind": {"single": 15, ...}}."""
    # TODO: collections.Counter
    ...


def generation_prompt(chunk_text, lang, n=3):
    """Ask for n questions a real client would ask, in lang ("en", "fr" or "ar"), that this passage answers.
    The reply must be a JSON list of objects {"question": ..., "answer": ...} and nothing else.
    Include the passage."""
    # TODO
    ...


def parse_generated(reply, chunk_id, lang):
    """Turn the model's reply into a list of TestItem.
    Models often wrap JSON in ```json fences or add a sentence: take the text from the first "[" to the last "]".
    Each object becomes TestItem(question=..., lang=lang, answer=..., source_ids=[chunk_id]).
    Anything unparseable or invalid -> [] (skip it, don't crash)."""
    # TODO
    ...


def dedupe(items):
    """Keep the first item for each question, comparing lowercase questions with punctuation removed
    (re.sub(r"[^\w\s]", "", q.lower()).strip())."""
    # TODO
    ...


if __name__ == "__main__":
    from bench_llm import get_client, current_model

    base = load_testset("../day21/questions.json")
    print("your 20:", summary(base))

    client = get_client()
    chunks = json.load(open("../day15/chunks.json", encoding="utf-8"))
    candidates = []
    for i, c in enumerate(chunks):
        lang = ("en", "fr", "ar")[i % 3]     # rotate languages: many questions cross languages
        msg = client.messages.create(model=current_model(), max_tokens=600, temperature=0.7,
                                     messages=[{"role": "user", "content": generation_prompt(c["text"], lang)}])
        candidates += parse_generated(msg.content[0].text, c["id"], lang)
    candidates = dedupe(base + candidates)[len(base):]
    json.dump([c.model_dump() for c in candidates], open("candidates.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"{len(candidates)} candidates in candidates.json. Review them, keep the good ones, fix wording,")
    print("then save your 20 + the kept ones (50 total) as testset_v1.json in this folder.")
