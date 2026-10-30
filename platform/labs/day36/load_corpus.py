"""A real Arabic corpus with real questions.

ARCD (Arabic Reading Comprehension Dataset) has Wikipedia paragraphs and ~1,400 questions
whose answers are in those paragraphs. That's exactly a RAG test set: documents to index,
questions to ask, and the right document for each question.

It's downloaded through the Hugging Face **datasets server**, a plain JSON API, so no
extra package is needed.

1. `rows_url`: the URL of one page of rows.
2. `fetch_rows`: download page after page (the server gives at most 100 rows per request).
3. `to_corpus`: turn rows into documents (one per distinct paragraph) and questions.
4. `save_jsonl` / `load_jsonl`: one JSON object per line, Arabic kept readable.

Running the file downloads the corpus into this folder (`arcd_docs.jsonl`,
`arcd_questions.jsonl`); days 38-41 use them. Without internet it shows a small sample.
"""
import json
from urllib.parse import urlencode

import httpx

API = "https://datasets-server.huggingface.co/rows"
DATASET, CONFIG = "hsseinmz/arcd", "plain_text"


def rows_url(dataset, config, split, offset, length):
    """The URL for one page of rows: `length` rows starting at row `offset`.

    `urlencode` builds the `?a=1&b=2` part and escapes special characters
    (the `/` in the dataset name becomes `%2F`).

    Example:
        >>> rows_url("hsseinmz/arcd", "plain_text", "train", 200, 100)
        'https://datasets-server.huggingface.co/rows?dataset=hsseinmz%2Farcd&config=plain_text&split=train&offset=200&length=100'
    """
    return f"{API}?" + urlencode({"dataset": dataset, "config": config, "split": split, "offset": offset, "length": length})


def fetch_rows(http, dataset, config, split, total, page=100):
    """Download `total` rows, `page` rows per request.

    `range(0, total, page)` gives the offsets 0, 100, 200, ... The last page
    asks only for what's left (`min(page, total - offset)`). If the server
    returns an empty page, the dataset has fewer rows than asked: stop.
    `raise_for_status()` turns an HTTP error (404, 500) into an exception
    instead of silently using a broken response.

    Example (a fake server with 250 rows):
        >>> from urllib.parse import parse_qs, urlparse
        >>> class Resp:
        ...     def __init__(self, rows): self.rows = rows
        ...     def raise_for_status(self): pass
        ...     def json(self): return {"rows": [{"row_idx": i, "row": r} for i, r in enumerate(self.rows)]}
        >>> class FakeHttp:
        ...     def __init__(self): self.data, self.calls = [{"i": i} for i in range(250)], 0
        ...     def get(self, url, timeout=None):
        ...         self.calls += 1
        ...         q = {k: int(v[0]) for k, v in parse_qs(urlparse(url).query).items() if k in ("offset", "length")}
        ...         return Resp(self.data[q["offset"]: q["offset"] + q["length"]])
        >>> http = FakeHttp()
        >>> rows = fetch_rows(http, "d", "c", "train", total=250)
        >>> len(rows), rows[-1], http.calls
        (250, {'i': 249}, 3)
    """
    out = []
    for offset in range(0, total, page):
        resp = http.get(rows_url(dataset, config, split, offset, min(page, total - offset)), timeout=60)
        resp.raise_for_status()
        rows = resp.json()["rows"]
        if not rows:
            break
        out += [r["row"] for r in rows]
    return out


def to_corpus(rows):
    """Split the rows into documents and questions.

    Several questions often share the same paragraph (`context`). Each
    distinct paragraph becomes **one** document with an id `d0`, `d1`, ...
    The dict `ids` remembers which paragraph already has which id. Each
    question keeps its first answer and points to its document in
    `source_ids`, which is what retrieval recall is measured against.

    Example:
        >>> rows = [{"title": "تونس", "context": "تونس عاصمة الجمهورية التونسية.", "question": "ما عاصمة تونس؟",
        ...          "answers": {"text": ["تونس"]}},
        ...         {"title": "تونس", "context": "تونس عاصمة الجمهورية التونسية.", "question": "تونس عاصمة أي دولة؟",
        ...          "answers": {"text": ["الجمهورية التونسية"]}},
        ...         {"title": "صفاقس", "context": "صفاقس مدينة ساحلية.", "question": "ما نوع مدينة صفاقس؟",
        ...          "answers": {"text": ["ساحلية"]}}]
        >>> docs, questions = to_corpus(rows)
        >>> [d["id"] for d in docs], [q["source_ids"] for q in questions]
        (['d0', 'd1'], [['d0'], ['d0'], ['d1']])
        >>> questions[2]
        {'question': 'ما نوع مدينة صفاقس؟', 'lang': 'ar', 'answer': 'ساحلية', 'source_ids': ['d1']}
    """
    ids, docs, questions = {}, [], []
    for r in rows:
        if r["context"] not in ids:
            ids[r["context"]] = f"d{len(docs)}"
            docs.append({"id": ids[r["context"]], "title": r["title"], "text": r["context"]})
        questions.append({"question": r["question"], "lang": "ar", "answer": r["answers"]["text"][0],
                          "source_ids": [ids[r["context"]]]})
    return docs, questions


def save_jsonl(items, path):
    """Write one JSON object per line (the JSONL format).

    JSONL is easy to append to and to read line by line, even for huge files.
    `ensure_ascii=False` writes Arabic as Arabic; without it, every letter
    would become an unreadable escape like `\\u062a`.

    Example:
        >>> import os, tempfile
        >>> path = os.path.join(tempfile.mkdtemp(), "x.jsonl")
        >>> save_jsonl([{"q": "ما عاصمة تونس؟"}, {"q": "Sousse?"}], path)
        >>> print(open(path, encoding="utf-8").read())
        {"q": "ما عاصمة تونس؟"}
        {"q": "Sousse?"}
        <BLANKLINE>
    """
    with open(path, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")


def load_jsonl(path):
    """Read a JSONL file back into a list of dicts, skipping empty lines.

    Example:
        >>> import os, tempfile
        >>> path = os.path.join(tempfile.mkdtemp(), "x.jsonl")
        >>> save_jsonl([{"id": "d0"}, {"id": "d1"}], path)
        >>> load_jsonl(path)
        [{'id': 'd0'}, {'id': 'd1'}]
    """
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


if __name__ == "__main__":
    try:
        rows = fetch_rows(httpx, DATASET, CONFIG, "train", total=700) + fetch_rows(httpx, DATASET, CONFIG, "validation", total=710)
    except httpx.HTTPError as e:
        print(f"Download failed ({type(e).__name__}), showing a small sample instead.\n")
        rows = [{"title": "تونس", "context": "تونس عاصمة الجمهورية التونسية وأكبر مدنها.", "question": "ما عاصمة تونس؟",
                 "answers": {"text": ["تونس"]}},
                {"title": "صفاقس", "context": "صفاقس مدينة ساحلية في الوسط الشرقي.", "question": "أين تقع صفاقس؟",
                 "answers": {"text": ["في الوسط الشرقي"]}}]
    docs, questions = to_corpus(rows)
    save_jsonl(docs, "arcd_docs.jsonl")
    save_jsonl(questions, "arcd_questions.jsonl")
    print(f"{len(rows)} rows -> {len(docs)} paragraphs, {len(questions)} questions")
    print(docs[0]["title"], "|", docs[0]["text"][:120])
    print(questions[0])
