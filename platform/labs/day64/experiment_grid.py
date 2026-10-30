"""Week 10 compares configurations: model x reranker x k x search type.

The grid grows fast (2 x 2 x 3 x 2 = 24 runs), each run takes minutes, and something
will crash halfway. So: expand the grid, drop combinations that make no sense, give each
run a stable key, log results as you go, and **resume** from the log after a crash.

1. `SPACE` and `RULES`: the options, and the combinations to skip.
2. `expand_grid` and `filter_valid`: every combination, then only the sensible ones.
3. `config_name` and `run_key`: a readable name and a stable id per run.
4. `load_done`, `append_result`, `pending`: the crash-safe log.
"""
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
    """Every combination of the options, as a list of dicts.

    `itertools.product(*space.values())` gives every tuple that takes one
    value from each list; `zip(keys, values)` turns a tuple back into a dict.

    Example:
        >>> expand_grid({"a": [1, 2], "b": ["x", "y"]})
        [{'a': 1, 'b': 'x'}, {'a': 1, 'b': 'y'}, {'a': 2, 'b': 'x'}, {'a': 2, 'b': 'y'}]
        >>> len(expand_grid(SPACE))
        24
    """
    keys = list(space)
    return [dict(zip(keys, values)) for values in itertools.product(*space.values())]


def filter_valid(configs, rules):
    """Keep the configs that pass every rule. Each rule is a function
    `config -> bool`, so a new constraint is one more lambda in `RULES`.

    Example:
        >>> filter_valid([{"k": 3, "rerank": True}, {"k": 5, "rerank": True}, {"k": 3, "rerank": False}], RULES)
        [{'k': 5, 'rerank': True}, {'k': 3, 'rerank': False}]
        >>> len(filter_valid(expand_grid(SPACE), RULES))
        20
    """
    return [c for c in configs if all(rule(c) for rule in rules)]


def config_name(config):
    """A readable name, the same whatever order the keys were written in
    (keys sorted). Used in tables and plots.

    Example:
        >>> config_name({"rerank": True, "k": 5, "model": "m"})
        'k=5|model=m|rerank=True'
    """
    return "|".join(f"{k}={config[k]}" for k in sorted(config))


def run_key(config, dataset_version):
    """A 12-hex id for "this config on this version of the test set".

    The data version is part of the key: change the golden set and every
    key changes, so everything re-runs. Results on old data never mix with new.

    Example:
        >>> run_key({"a": 1, "b": 2}, "v1") == run_key({"b": 2, "a": 1}, "v1")
        True
        >>> run_key({"a": 1}, "v1") == run_key({"a": 1}, "v2")
        False
    """
    return hashlib.sha1(json.dumps({"config": config, "data": dataset_version}, sort_keys=True).encode()).hexdigest()[:12]


def load_done(path):
    """The run keys already in the JSONL log. A missing file means nothing ran.

    If the program crashed while writing, the last line is cut in half:
    `json.loads` fails on it and it's skipped (that run simply runs again).

    Example:
        >>> import tempfile
        >>> log = Path(tempfile.mkdtemp()) / "runs.jsonl"
        >>> load_done(log)
        set()
        >>> _ = log.write_text('{"key": "k1"}\\n{"key": "k2"}\\n{"key": "k3", "metr', encoding="utf-8")
        >>> sorted(load_done(log))
        ['k1', 'k2']
    """
    path = Path(path)
    if not path.exists():
        return set()
    done = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            done.add(json.loads(line)["key"])
        except (json.JSONDecodeError, KeyError):
            continue
    return done


def append_result(path, record):
    """Append one JSON line right after each run, and flush it to disk.

    Mode `"a"` adds to the end of the file. If run 15 of 20 crashes, runs
    1-14 are safe in the log.

    Example:
        >>> import tempfile
        >>> log = Path(tempfile.mkdtemp()) / "runs.jsonl"
        >>> append_result(log, {"key": "k1", "name": "été"})
        >>> append_result(log, {"key": "k2"})
        >>> print(log.read_text(encoding="utf-8"))
        {"key": "k1", "name": "été"}
        {"key": "k2"}
        <BLANKLINE>
    """
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
        f.flush()


def pending(configs, done, dataset_version):
    """The configs still to run: those whose key isn't in the log yet.

    Example:
        >>> cfgs = [{"k": 3}, {"k": 5}, {"k": 10}]
        >>> pending(cfgs, {run_key({"k": 5}, "v1")}, "v1")
        [{'k': 3}, {'k': 10}]
        >>> len(pending(cfgs, {run_key({"k": 5}, "v1")}, "v2"))
        3
    """
    return [c for c in configs if run_key(c, dataset_version) not in done]


def run_grid(evaluate, log="runs.jsonl", data_version=None):
    """Run every pending config with your `evaluate(config) -> metrics`.

    The real `evaluate` is your Week 4 `run_eval` loop with this config wired
    into the day 55 pipeline. The data version is the hash of day 48's dev set.

    Example (note): needs your evaluate function and ../day48/golden_dev.jsonl.
        >>> run_grid(my_evaluate)  # doctest: +SKIP
    """
    if data_version is None:
        data_version = hashlib.sha1(Path("../day48/golden_dev.jsonl").read_bytes()).hexdigest()[:8]
    configs = filter_valid(expand_grid(SPACE), RULES)
    todo = pending(configs, load_done(log), data_version)
    print(len(configs), "valid configs,", len(todo), "to run on data", data_version)
    for c in todo:
        append_result(log, {"key": run_key(c, data_version), "name": config_name(c), "config": c, "metrics": evaluate(c)})
        print("done", config_name(c))


if __name__ == "__main__":
    # Demo: a fake evaluate that crashes on the 7th run, then a second run that resumes.
    import random
    import tempfile
    log = Path(tempfile.mkdtemp()) / "runs.jsonl"
    calls = {"n": 0}

    def evaluate(c):
        calls["n"] += 1
        if calls["n"] == 7:
            raise RuntimeError("Ollama crashed")
        rng = random.Random(config_name(c))
        return {"correct": round(0.6 + 0.1 * c["rerank"] + 0.05 * (c["search"] == "hybrid") + rng.uniform(0, 0.1), 2)}

    try:
        run_grid(evaluate, log, data_version="demo")
    except RuntimeError as e:
        print("CRASH:", e, "| lines in the log:", len(load_done(log)))
    print("\n--- run again: it resumes ---")
    run_grid(evaluate, log, data_version="demo")
    best = max((json.loads(l) for l in log.read_text(encoding="utf-8").splitlines()), key=lambda r: r["metrics"]["correct"])
    print("\nbest:", best["name"], best["metrics"])
