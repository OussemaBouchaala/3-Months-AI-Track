"""The eval harness: every configuration, the same questions, one table.

To choose between RAG setups (vector or hybrid search, 3 or 5 chunks, rerank or not),
you change **one thing at a time**, run the **same** questions through each setup,
and compare them in one table.

1. `config_grid`: every combination of settings (2 x 2 x 2 = 8 configs).
2. `run_config`: runs one config on all questions and averages the scores into one row.
3. `results_table`: the rows as a Markdown table, best first.
4. `pick_best`: the most correct config that is still fast enough.
5. `run_on_my_pipeline`: the same harness wired to the real RAG from days 15-24.

Running the file uses a small **simulated** pipeline, so you see the whole flow in seconds.
"""
import itertools
import statistics


def config_grid(retrievers=("vector", "hybrid"), ks=(3, 5), reranks=(False, True)):
    """Every combination of settings, as a list of dicts.

    `itertools.product` gives every combination of the three lists, like
    nested for loops. Each config gets a readable name such as
    `"hybrid-k5-rerank"` so it can label a row of the results table.

    Example:
        >>> grid = config_grid()
        >>> len(grid)
        8
        >>> [c["name"] for c in grid][:3]
        ['vector-k3-norerank', 'vector-k3-rerank', 'vector-k5-norerank']
        >>> grid[-1]
        {'name': 'hybrid-k5-rerank', 'retriever': 'hybrid', 'k': 5, 'rerank': True}
    """
    return [{"name": f"{r}-k{k}-{'rerank' if rr else 'norerank'}", "retriever": r, "k": k, "rerank": rr}
            for r, k, rr in itertools.product(retrievers, ks, reranks)]


def run_config(config, items, answer_fn, grade_fn):
    """Run one config on every test question and summarize it as one row.

    For each item:
    - `answer_fn(question, config)` runs the pipeline and returns the answer,
      the ids of the chunks it retrieved, the sources text, seconds and cost.
    - `grade_fn(item, answer, sources_text)` returns `{"correct": 0/1, "faithful": 0/1}`.

    The row holds:
    - **recall**: of the chunks that hold the answer (`source_ids`), the share
      that was retrieved. Only answerable items count (an unanswerable item has
      no source to find).
    - **correct**, **faithful**: averages of the grades.
    - **p95**: the 95th-percentile seconds. **cost_1k**: dollars per 1,000 queries.

    Example (3 questions, a fake pipeline and a fake grader):
        >>> items = [{"question": "q1", "source_ids": ["a"]},
        ...          {"question": "q2", "source_ids": ["b", "c"]},
        ...          {"question": "q3", "source_ids": []}]
        >>> outs = {"q1": {"answer": "A1", "retrieved": ["a", "z"], "sources_text": "", "seconds": 1.0, "cost": 0.002},
        ...         "q2": {"answer": "A2", "retrieved": ["b", "z"], "sources_text": "", "seconds": 2.0, "cost": 0.004},
        ...         "q3": {"answer": "A3", "retrieved": ["z"], "sources_text": "", "seconds": 3.0, "cost": 0.003}}
        >>> grades = {"A1": {"correct": 1, "faithful": 1}, "A2": {"correct": 0, "faithful": 1},
        ...           "A3": {"correct": 1, "faithful": 0}}
        >>> row = run_config({"name": "demo"}, items, lambda q, c: outs[q], lambda it, a, s: grades[a])
        >>> {k: round(v, 2) if isinstance(v, float) else v for k, v in row.items()}
        {'config': 'demo', 'n': 3, 'recall': 0.75, 'correct': 0.67, 'faithful': 0.67, 'p95': 2.9, 'cost_1k': 3.0}
    """
    recalls, correct, faithful, secs, costs = [], [], [], [], []
    for it in items:
        out = answer_fn(it["question"], config)
        g = grade_fn(it, out["answer"], out["sources_text"])
        if it["source_ids"]:
            recalls.append(len(set(it["source_ids"]) & set(out["retrieved"])) / len(it["source_ids"]))
        correct.append(g["correct"])
        faithful.append(g["faithful"])
        secs.append(out["seconds"])
        costs.append(out["cost"])
    return {"config": config["name"], "n": len(items), "recall": statistics.mean(recalls),
            "correct": statistics.mean(correct), "faithful": statistics.mean(faithful),
            "p95": statistics.quantiles(secs, n=100, method="inclusive")[94], "cost_1k": 1000 * statistics.mean(costs)}


def results_table(rows):
    """The rows as a Markdown table, the most correct config first.

    `sorted(rows, key=lambda r: -r["correct"])` sorts from high to low
    (the minus sign flips the order). `:.2f` prints numbers with 2 decimals.

    Example:
        >>> rows = [{"config": "fast", "n": 50, "recall": 0.8, "correct": 0.8, "faithful": 0.9, "p95": 2.0, "cost_1k": 1.0},
        ...         {"config": "slow", "n": 50, "recall": 0.9, "correct": 0.9, "faithful": 0.95, "p95": 7.0, "cost_1k": 2.0}]
        >>> print(results_table(rows))
        | config | n | recall | correct | faithful | p95 (s) | $ / 1k |
        |---|---|---|---|---|---|---|
        | slow | 50 | 0.90 | 0.90 | 0.95 | 7.00 | 2.00 |
        | fast | 50 | 0.80 | 0.80 | 0.90 | 2.00 | 1.00 |
        <BLANKLINE>
    """
    out = "| config | n | recall | correct | faithful | p95 (s) | $ / 1k |\n|---|---|---|---|---|---|---|\n"
    for r in sorted(rows, key=lambda r: -r["correct"]):
        out += (f"| {r['config']} | {r['n']} | {r['recall']:.2f} | {r['correct']:.2f} | {r['faithful']:.2f} "
                f"| {r['p95']:.2f} | {r['cost_1k']:.2f} |\n")
    return out


def pick_best(rows, max_p95):
    """The most correct config whose p95 is within the latency limit.

    First keep only the rows fast enough. Then `max` with the key
    `(correct, -cost_1k)` picks the highest `correct`; if two tie, the
    higher `-cost`, which means the **cheaper** one. `None` if nothing is fast enough.

    Example:
        >>> rows = [{"config": "slow-good", "correct": 0.9, "p95": 7.0, "cost_1k": 2.0},
        ...         {"config": "fast-ok", "correct": 0.8, "p95": 2.0, "cost_1k": 1.0},
        ...         {"config": "fast-ok-cheap", "correct": 0.8, "p95": 2.5, "cost_1k": 0.5}]
        >>> pick_best(rows, max_p95=5.0)["config"]
        'fast-ok-cheap'
        >>> pick_best(rows, max_p95=10.0)["config"]
        'slow-good'
        >>> print(pick_best(rows, max_p95=1.0))
        None
    """
    ok = [r for r in rows if r["p95"] <= max_p95]
    return max(ok, key=lambda r: (r["correct"], -r["cost_1k"])) if ok else None


def run_on_my_pipeline():
    """The same harness, wired to your real RAG from days 15-24 (needs those files and an AI key).

    It builds `answer_fn` from your real pieces (embedding search, BM25 +
    RRF for hybrid, the LLM reranker, the RAG prompt) and grades with the
    LLM judge from day 24. It writes `eval_results.md` (the table) and
    `per_question.json` (every answer of the best config, used on day 28).
    """
    import json
    import sys
    import time

    sys.path += ["../day16", "../day18", "../day19", "../day20", "../day24"]
    import numpy as np
    from bench_llm import current_model, get_client
    from embed import embed, normalize, search
    from hybrid import bm25_scores, rank_ids, rrf
    from judge import grade
    from rag import build_prompt, format_context
    from rerank import parse_score, rerank, score_prompt

    chunks = json.load(open("../day15/chunks.json", encoding="utf-8"))
    by_id = {c["id"]: c for c in chunks}
    ids, texts = list(by_id), [c["text"] for c in chunks]
    matrix = np.load("../day16/embeddings.npy")
    items = json.load(open("../day22/testset_v1.json", encoding="utf-8"))
    client = get_client()

    def llm(prompt, max_tokens=300):
        msg = client.messages.create(model=current_model(), max_tokens=max_tokens, temperature=0,
                                     messages=[{"role": "user", "content": prompt}])
        return msg.content[0].text, msg.usage.input_tokens, msg.usage.output_tokens

    def answer_fn(question, cfg):
        start = time.perf_counter()
        vector = [ids[i] for i, _ in search(normalize(embed([question]))[0], matrix, k=len(ids))]
        ranked = rrf([rank_ids(ids, bm25_scores(question, texts)), vector]) if cfg["retriever"] == "hybrid" else vector
        cands = [by_id[i] for i in ranked[:10]]
        if cfg["rerank"]:
            cands = rerank(question, cands, lambda q, t: parse_score(llm(score_prompt(q, t), 5)[0]), top_n=cfg["k"])
        top = cands[:cfg["k"]]
        text, tin, tout = llm(build_prompt(question, top))
        return {"answer": text, "retrieved": [c["id"] for c in top], "sources_text": format_context(top),
                "seconds": time.perf_counter() - start, "cost": (tin * 0.30 + tout * 2.50) / 1e6}

    logs = {}

    def logged(cfg):
        def a(question, c):
            out = answer_fn(question, c)
            logs.setdefault(c["name"], []).append({"question": question, "answer": out["answer"], "retrieved": out["retrieved"]})
            return out

        def g(item, answer, sources):
            r = grade(item, answer, sources, lambda p: llm(p, 150)[0])
            logs[cfg["name"]][-1].update(correct=r["correct"], faithful=r["faithful"])
            return r
        return a, g

    rows = [run_config(cfg, items, *logged(cfg)) for cfg in config_grid()]
    table = results_table(rows)
    print(table)
    open("eval_results.md", "w", encoding="utf-8").write(table)
    best = pick_best(rows, max_p95=5.0) or max(rows, key=lambda r: r["correct"])
    print("best under 5 s p95:", best)
    json.dump(logs[best["config"]], open("per_question.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    import random

    # A simulated pipeline: hybrid finds more sources, rerank is more accurate but slower.
    random.seed(7)
    items = [{"question": f"q{i}", "source_ids": [f"c{i}"] if i % 10 else []} for i in range(50)]

    def answer_fn(question, cfg):
        found = random.random() < (0.85 if cfg["retriever"] == "hybrid" else 0.7) + 0.03 * (cfg["k"] == 5)
        i = question[1:]
        return {"answer": "...", "retrieved": [f"c{i}"] if found else ["other"], "sources_text": "",
                "seconds": random.uniform(1, 2) + (random.uniform(1, 3) if cfg["rerank"] else 0),
                "cost": 0.0009 + (0.0006 if cfg["rerank"] else 0) + 0.0002 * (cfg["k"] == 5),
                "_good": found and random.random() < (0.9 if cfg["rerank"] else 0.8)}

    last = {}

    def fake_answer(question, cfg):
        last.update(answer_fn(question, cfg))
        return last

    def fake_grade(item, answer, sources):
        ok = last["_good"] or not item["source_ids"]
        return {"correct": int(ok), "faithful": int(ok or random.random() < 0.5)}

    rows = [run_config(cfg, items, fake_answer, fake_grade) for cfg in config_grid()]
    print(results_table(rows))
    print("best under 4 s p95:", pick_best(rows, max_p95=4.0)["config"])
    print("\nTo run on your real RAG: call run_on_my_pipeline() (needs days 15-24 and an AI key).")
    run_on_my_pipeline()