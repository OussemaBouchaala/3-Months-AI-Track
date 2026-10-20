import json
import os
import tempfile

from pydantic import ValidationError

TestItem = var("TestItem")
check("TestItem has the four fields", lambda: set(TestItem.model_fields) == {"question", "lang", "answer", "source_ids"})


def _raises(f):
    try:
        f()
    except ValidationError:
        return True
    return False


check("TestItem rejects lang 'de'", lambda: _raises(lambda: TestItem(question="q", lang="de", answer="", source_ids=[])),
      'lang: Literal["en", "fr", "ar"]')


mk = lambda ids, lang="en", q="q?": TestItem(question=q, lang=lang, answer="a" if ids else "", source_ids=ids)
check("kind: unanswerable / single / multi", lambda: [fn("kind")(mk([])), fn("kind")(mk(["c1"])), fn("kind")(mk(["c1", "c2"]))] == ["unanswerable", "single", "multi"])


def tmp_json(data):
    path = os.path.join(tempfile.mkdtemp(), "t.json")
    json.dump(data, open(path, "w", encoding="utf-8"))
    return path


good = [{"question": "Q1?", "lang": "fr", "answer": "A", "source_ids": ["c1"]}, {"question": "Q2?", "lang": "ar", "answer": "", "source_ids": []}]
check("load_testset returns TestItem objects", lambda: all(isinstance(i, TestItem) for i in fn("load_testset")(tmp_json(good))))
check("load_testset stops on an invalid item", lambda: _raises(lambda: fn("load_testset")(tmp_json(good + [{"question": "x"}]))),
      "Don't catch ValidationError here: a broken test set must stop the eval.")
check("summary counts by lang and kind", lambda: fn("summary")([mk(["c1"], "fr"), mk([], "fr"), mk(["c1", "c2"], "ar")])
      == {"lang": {"fr": 2, "ar": 1}, "kind": {"single": 1, "unanswerable": 1, "multi": 1}})

gp = lambda: fn("generation_prompt")("Visits are free.", "fr", n=4)
check("generation_prompt includes the passage, the count and the language", lambda: "Visits are free." in gp() and "4" in gp() and ("fr" in gp() or "French" in gp() or "français" in gp()))
check("generation_prompt asks for a JSON list", lambda: "json" in gp().lower())
pg = fn("parse_generated")
reply = 'Here:\n```json\n[{"question": "Les visites sont payantes ?", "answer": "Non"}, {"question": "Horaires ?", "answer": "9h-18h"}]\n```'
check("parse_generated reads JSON inside fences and text", lambda: [i.question for i in pg(reply, "c3", "fr")] == ["Les visites sont payantes ?", "Horaires ?"])
check("parse_generated sets source_ids and lang", lambda: pg(reply, "c3", "fr")[0].source_ids == ["c3"] and pg(reply, "c3", "fr")[0].lang == "fr")
check("parse_generated returns [] on garbage", lambda: pg("I can't do that", "c3", "fr") == [] and pg("[{broken", "c3", "fr") == [])
check("parse_generated skips invalid objects", lambda: len(pg('[{"question": "ok?", "answer": "y"}, {"nope": 1}]', "c1", "en")) == 1)
dd = fn("dedupe")
check("dedupe ignores case and punctuation, keeps the first",
      lambda: [i.question for i in dd([mk(["c1"], q="Can I visit?"), mk(["c2"], q="can i visit"), mk(["c3"], q="Pets?")])] == ["Can I visit?", "Pets?"])
