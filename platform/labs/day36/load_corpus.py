# A real Arabic corpus with real questions: ARCD (Arabic Reading Comprehension Dataset, from Wikipedia).
# Downloaded through the Hugging Face "datasets server" JSON API: plain HTTP, no extra package.
# Check uses a fake HTTP client. Run downloads ~1,400 questions into this folder.
import json

import httpx

API = "https://datasets-server.huggingface.co/rows"
DATASET, CONFIG = "hsseinmz/arcd", "plain_text"


def rows_url(dataset, config, split, offset, length):
    """The datasets-server URL for one page of rows:
    {API}?dataset=<dataset>&config=<config>&split=<split>&offset=<offset>&length=<length>"""
    # TODO
    ...


def fetch_rows(http, dataset, config, split, total, page=100):
    """Download `total` rows, `page` at a time (the server allows at most 100 per request).
    http.get(url, timeout=60) returns a response whose .json() is {"rows": [{"row_idx": 0, "row": {...}}, ...]}.
    Return the list of the inner "row" dicts, in order. Stop early if a page comes back empty."""
    # TODO
    ...


def to_corpus(rows):
    """ARCD rows look like {"id", "title", "context", "question", "answers": {"text": [...], "answer_start": [...]}}.
    Many questions share the same context paragraph.
    Return (docs, questions):
      docs: one per DISTINCT context, in first-seen order: {"id": "d0", "title": ..., "text": context}
      questions: one per row: {"question": ..., "lang": "ar", "answer": answers["text"][0], "source_ids": [<doc id of its context>]}"""
    # TODO
    ...


def save_jsonl(items, path):
    """One JSON object per line, ensure_ascii=False (keep Arabic readable), UTF-8."""
    # TODO
    ...


def load_jsonl(path):
    # TODO
    ...


if __name__ == "__main__":
    rows = fetch_rows(httpx, DATASET, CONFIG, "train", total=700) + fetch_rows(httpx, DATASET, CONFIG, "validation", total=710)
    docs, questions = to_corpus(rows)
    save_jsonl(docs, "arcd_docs.jsonl")
    save_jsonl(questions, "arcd_questions.jsonl")
    print(f"{len(rows)} rows -> {len(docs)} paragraphs, {len(questions)} questions")
    print(docs[0]["title"], "|", docs[0]["text"][:120])
    print(questions[0])
