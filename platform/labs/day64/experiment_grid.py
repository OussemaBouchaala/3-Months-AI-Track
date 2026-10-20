# Week 10 compares configurations: model x reranker x k x ... The grid grows fast, runs take minutes each,
# and something will crash halfway. So: expand, drop impossible combos, name each run, and resume from a log.
import hashlib
import itertools
import json
from pathlib import Path

SPACE = {
    "model": ["qwen2.5:7b (local)", "claude-haiku (API)"],
    "rerank": [False, True],
    "k": [3, 5, 10],
    "search": ["vector", "hybrid"],
}
RULES = [
    lambda c: not (c["rerank"] and c["k"] < 5),          # reranking 3 chunks changes almost nothing
]


def expand_grid(space):
    """Every combination as a dict, in itertools.product order over the keys as given."""
    # TODO
    ...


def filter_valid(configs, rules):
    """Keep configs for which every rule returns True."""
    # TODO
    ...


def config_name(config):
    """Readable and stable: keys sorted, "k=5|model=qwen2.5:7b (local)|rerank=True|search=hybrid"."""
    # TODO
    ...


def run_key(config, dataset_version):
    """First 12 hex of sha1 of json.dumps({"config": config, "data": dataset_version}, sort_keys=True).
    Change the golden set -> new keys -> everything re-runs; that's the point."""
    # TODO
    ...


def load_done(path):
    """Set of run keys already in the JSONL log (one {"key", ...} per line). Missing file -> empty set.
    Ignore a broken last line (the crash happened mid-write)."""
    # TODO
    ...


def append_result(path, record):
    """Append one JSON line (ensure_ascii=False) and flush, so a crash loses at most the current run."""
    # TODO
    ...


def pending(configs, done, dataset_version):
    """Configs whose run_key is not in done, in order."""
    # TODO
    ...


if __name__ == "__main__":
    import sys
    sys.path += ["../day46"]
    configs = filter_valid(expand_grid(SPACE), RULES)
    data_version = hashlib.sha1(Path("../day48/golden_dev.jsonl").read_bytes()).hexdigest()[:8]
    todo = pending(configs, load_done("runs.jsonl"), data_version)
    print(len(configs), "valid configs,", len(todo), "to run on data", data_version)
    for c in todo:
        # metrics = evaluate(c)   <- your Week 4 run_eval loop, with this config wired into the day55 pipeline
        metrics = {"todo": True}
        append_result("runs.jsonl", {"key": run_key(c, data_version), "name": config_name(c), "config": c, "metrics": metrics})
        print("done", config_name(c))
