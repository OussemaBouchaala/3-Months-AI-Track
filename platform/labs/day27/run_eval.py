# The eval harness: every configuration, the same 50 questions, one table.
# Check uses a fake pipeline. Run wires your real one (see the bottom of the file).
import itertools
import statistics


def config_grid(retrievers=("vector", "hybrid"), ks=(3, 5), reranks=(False, True)):
    """Every combination as a dict {"name", "retriever", "k", "rerank"}, in itertools.product order.
    name looks like "hybrid-k5-rerank" or "vector-k3-norerank"."""
    # TODO
    ...


def run_config(config, items, answer_fn, grade_fn):
    """For each item: out = answer_fn(item["question"], config) returns
        {"answer": str, "retrieved": [ids actually given to the model], "sources_text": str, "seconds": float, "cost": float}
    and g = grade_fn(item, out["answer"], out["sources_text"]) returns {"correct": 0/1, "faithful": 0/1, ...}.
    Return one row:
        {"config": name, "n": number of items,
         "recall": mean over ANSWERABLE items of |source_ids ∩ retrieved| / |source_ids|,
         "correct": mean correct, "faithful": mean faithful,
         "p95": 95th percentile of seconds (statistics.quantiles(..., n=100, method="inclusive")[94]),
         "cost_1k": 1000 * mean cost}"""
    # TODO
    ...


def results_table(rows):
    """Markdown table sorted by correct (best first):
    | config | n | recall | correct | faithful | p95 (s) | $ / 1k |
    numbers with 2 decimals."""
    # TODO
    ...


def pick_best(rows, max_p95):
    """Among rows with p95 <= max_p95, the highest correct; ties -> the cheaper one. None if no row qualifies."""
    # TODO
    ...


if __name__ == "__main__":
    import json
    import sys
    import time

    sys.path += ["../day16", "../day18", "../day19", "../day20", "../day24"]
    import numpy as np
    from bench_llm import get_client, current_model
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

    grade_fn = lambda item, answer, sources: grade(item, answer, sources, lambda p: llm(p, 150)[0])
    logs = {}   # per-question records for each config, for Sunday's error analysis

    def logged(cfg):
        def a(question, c):
            out = answer_fn(question, c)
            logs.setdefault(c["name"], []).append({"question": question, "answer": out["answer"], "retrieved": out["retrieved"]})
            return out

        def g(item, answer, sources):
            r = grade_fn(item, answer, sources)
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
