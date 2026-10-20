grid = lambda: fn("config_grid")(("vector", "hybrid"), (3, 5), (False, True))
check("config_grid makes every combination", lambda: len(grid()) == 8 and len({c["name"] for c in grid()}) == 8)
check("names look like hybrid-k5-rerank", lambda: {"vector-k3-norerank", "hybrid-k5-rerank"} <= {c["name"] for c in grid()}
      and grid()[0] == {"name": "vector-k3-norerank", "retriever": "vector", "k": 3, "rerank": False})

items = [{"question": "q1", "source_ids": ["a"], "answer": "x"},
         {"question": "q2", "source_ids": ["b", "c"], "answer": "y"},
         {"question": "q3", "source_ids": [], "answer": ""}]
outs = {"q1": {"answer": "A1", "retrieved": ["a", "z"], "sources_text": "S1", "seconds": 1.0, "cost": 0.002},
        "q2": {"answer": "A2", "retrieved": ["b", "z"], "sources_text": "S2", "seconds": 2.0, "cost": 0.004},
        "q3": {"answer": "A3", "retrieved": ["z"], "sources_text": "S3", "seconds": 3.0, "cost": 0.003}}
grades = {"A1": {"correct": 1, "faithful": 1}, "A2": {"correct": 0, "faithful": 1}, "A3": {"correct": 1, "faithful": 0}}
seen = []


def answer_fn(q, cfg):
    seen.append(cfg["name"])
    return outs[q]


def grade_fn(item, answer, sources):
    assert sources == outs[item["question"]]["sources_text"], "grade_fn must get the sources_text"
    return grades[answer]


row = lambda: fn("run_config")({"name": "hybrid-k3-rerank", "retriever": "hybrid", "k": 3, "rerank": True}, items, answer_fn, grade_fn)
check("run_config passes the config and returns its name and n", lambda: row()["config"] == "hybrid-k3-rerank" and row()["n"] == 3 and "hybrid-k3-rerank" in seen)
check("recall only counts answerable items", lambda: abs(row()["recall"] - 0.75) < 1e-9, "q1: 1/1, q2: 1/2, q3 skipped -> 0.75")
check("correct and faithful are means", lambda: abs(row()["correct"] - 2 / 3) < 1e-9 and abs(row()["faithful"] - 2 / 3) < 1e-9)
check("p95 and cost_1k", lambda: abs(row()["p95"] - 2.9) < 1e-9 and abs(row()["cost_1k"] - 3.0) < 1e-9)

rows = [{"config": "slow-good", "n": 50, "recall": 0.9, "correct": 0.9, "faithful": 0.95, "p95": 7.0, "cost_1k": 2.0},
        {"config": "fast-ok", "n": 50, "recall": 0.8, "correct": 0.8, "faithful": 0.9, "p95": 2.0, "cost_1k": 1.0},
        {"config": "fast-ok-cheap", "n": 50, "recall": 0.8, "correct": 0.8, "faithful": 0.9, "p95": 2.5, "cost_1k": 0.5}]
lines = lambda: [l for l in fn("results_table")(rows).strip().splitlines() if l.strip()]
check("results_table: header, separator, one line per config", lambda: len(lines()) == 5 and lines()[0].count("|") >= 8)
check("results_table sorts by correct, 2 decimals", lambda: "slow-good" in lines()[2] and "0.90" in lines()[2] and "7.00" in lines()[2])
pb = fn("pick_best")
check("pick_best respects the latency limit, ties go to the cheaper", lambda: pb(rows, 5.0)["config"] == "fast-ok-cheap")
check("pick_best with a loose limit takes the most correct", lambda: pb(rows, 10.0)["config"] == "slow-good")
check("pick_best returns None if nothing qualifies", lambda: pb(rows, 1.0) is None and pb(rows, 10.0) is not None)
