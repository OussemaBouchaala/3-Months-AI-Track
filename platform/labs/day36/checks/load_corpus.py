from urllib.parse import parse_qs, urlparse
import os
import tempfile

u = lambda: fn("rows_url")("hsseinmz/arcd", "plain_text", "train", 200, 100)
check("rows_url points to the datasets-server rows API", lambda: u().startswith("https://datasets-server.huggingface.co/rows?"))
check("rows_url has every parameter", lambda: {k: v[0] for k, v in parse_qs(urlparse(u()).query).items()} == {"dataset": "hsseinmz/arcd", "config": "plain_text", "split": "train", "offset": "200", "length": "100"})


class Resp:
    def __init__(self, rows):
        self.rows = rows

    def raise_for_status(self):
        pass

    def json(self):
        return {"rows": [{"row_idx": i, "row": r} for i, r in enumerate(self.rows)]}


class FakeHttp:
    def __init__(self, n):
        self.data, self.urls = [{"i": i} for i in range(n)], []

    def get(self, url, timeout=None, **kw):
        self.urls.append(url)
        q = {k: int(v[0]) for k, v in parse_qs(urlparse(url).query).items() if k in ("offset", "length")}
        return Resp(self.data[q["offset"]: q["offset"] + q["length"]])


h = FakeHttp(250)
got = lambda: fn("fetch_rows")(h, "d", "c", "train", total=250, page=100)
check("fetch_rows pages through offsets 0, 100, 200", lambda: (h.urls.clear(), got())[1] == [{"i": i} for i in range(250)] and len(h.urls) == 3)
h2 = FakeHttp(120)
check("fetch_rows stops when a page is empty", lambda: len(fn("fetch_rows")(h2, "d", "c", "train", total=500, page=100)) == 120 and len(h2.urls) <= 3)

rows = [{"id": "1", "title": "تونس", "context": "تونس عاصمة الجمهورية التونسية.", "question": "ما عاصمة تونس؟", "answers": {"text": ["تونس"], "answer_start": [0]}},
        {"id": "2", "title": "تونس", "context": "تونس عاصمة الجمهورية التونسية.", "question": "تونس عاصمة أي دولة؟", "answers": {"text": ["الجمهورية التونسية"], "answer_start": [12]}},
        {"id": "3", "title": "صفاقس", "context": "صفاقس مدينة ساحلية.", "question": "ما نوع مدينة صفاقس؟", "answers": {"text": ["ساحلية"], "answer_start": [12]}}]
tc = lambda: fn("to_corpus")(rows)
check("to_corpus deduplicates contexts", lambda: tc()[0] == [{"id": "d0", "title": "تونس", "text": "تونس عاصمة الجمهورية التونسية."}, {"id": "d1", "title": "صفاقس", "text": "صفاقس مدينة ساحلية."}])
check("to_corpus links each question to its document", lambda: [q["source_ids"] for q in tc()[1]] == [["d0"], ["d0"], ["d1"]])
check("questions use the first answer and lang 'ar'", lambda: tc()[1][1] == {"question": "تونس عاصمة أي دولة؟", "lang": "ar", "answer": "الجمهورية التونسية", "source_ids": ["d0"]})
p = os.path.join(tempfile.mkdtemp(), "x.jsonl")
check("save_jsonl / load_jsonl round-trip Arabic", lambda: (fn("save_jsonl")(tc()[1], p), fn("load_jsonl")(p))[1] == tc()[1])
check("save_jsonl keeps Arabic readable (ensure_ascii=False)", lambda: (fn("save_jsonl")(tc()[1], p), "تونس" in open(p, encoding="utf-8").read())[1])
check("one object per line", lambda: (fn("save_jsonl")(tc()[1], p), len(open(p, encoding="utf-8").read().strip().splitlines()))[1] == 3)
