IDK = var("IDK")
jp = lambda: fn("judge_prompt")("Rent +8%?", "No, max 5%.", "Yes, 8% [1].", "Max 5% per year.")
check("judge_prompt includes question, expected, answer and sources",
      lambda: all(s in jp() for s in ("Rent +8%?", "No, max 5%.", "Yes, 8% [1].", "Max 5% per year.")))
check("judge_prompt asks for correct, faithful and reason as JSON", lambda: all(s in jp() for s in ('"correct"', '"faithful"', '"reason"')))
pj = fn("parse_judgment")
check("parse_judgment reads JSON with text around it",
      lambda: pj('Verdict:\n{"correct": 1, "faithful": 0, "reason": "adds 8%"}\nThanks') == {"correct": 1, "faithful": 0, "reason": "adds 8%"})
check("parse_judgment turns true / '1' into 1", lambda: pj('{"correct": true, "faithful": "1", "reason": "ok"}')[ "correct"] == 1 and pj('{"correct": true, "faithful": "1", "reason": "ok"}')["faithful"] == 1)
check("parse_judgment has a safe default", lambda: pj("looks fine to me") == {"correct": 0, "faithful": 0, "reason": "unparseable judge reply"})

calls = []


def judge_says(reply):
    def model(prompt):
        calls.append(prompt)
        return reply
    return model


un = {"question": "Cars?", "answer": "", "source_ids": []}
ans = {"question": "Rent +8%?", "answer": "No, max 5%.", "source_ids": ["c6"]}
g = fn("grade")
check("unanswerable + IDK -> correct, no model call", lambda: (calls.clear(), g(un, IDK, "", judge_says("x")))[1]["correct"] == 1 and calls == [])
check("unanswerable + invented answer -> 0, 0", lambda: (lambda r: r["correct"] == 0 and r["faithful"] == 0)(g(un, "Yes we sell cars [1].", "", judge_says("x"))))
check("answerable + IDK -> 'false IDK', no model call",
      lambda: (calls.clear(), g(ans, IDK, "src", judge_says("x")))[1] == {"correct": 0, "faithful": 1, "reason": "false IDK"} and calls == [])
check("answerable -> the judge decides", lambda: g(ans, "No [1].", "Max 5% per year.", judge_says('{"correct": 1, "faithful": 1, "reason": "ok"}'))["correct"] == 1
      and "Max 5% per year." in calls[-1])
