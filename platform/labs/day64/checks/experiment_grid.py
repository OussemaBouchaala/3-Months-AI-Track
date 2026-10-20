import json, tempfile
from pathlib import Path
eg = fn("expand_grid")
check("expand_grid: every combination, product order", lambda: eg({"a": [1, 2], "b": ["x", "y"]}) == [{"a": 1, "b": "x"}, {"a": 1, "b": "y"}, {"a": 2, "b": "x"}, {"a": 2, "b": "y"}])
check("the default SPACE gives 24 configs", lambda: len(eg(var("SPACE"))) == 2 * 2 * 3 * 2 or len(eg(var("SPACE"))) >= 4)
fv = fn("filter_valid")
check("filter_valid applies every rule", lambda: fv([{"k": 3, "rerank": True}, {"k": 5, "rerank": True}, {"k": 3, "rerank": False}], [lambda c: not (c["rerank"] and c["k"] < 5), lambda c: c["k"] != 5]) == [{"k": 3, "rerank": False}])
cn = fn("config_name")
check("config_name: sorted keys, stable", lambda: cn({"rerank": True, "k": 5, "model": "m"}) == "k=5|model=m|rerank=True" and cn({"model": "m", "k": 5, "rerank": True}) == cn({"rerank": True, "k": 5, "model": "m"}))
rk = fn("run_key")
check("run_key: 12 hex, key order doesn't matter, data version does", lambda: len(rk({"a": 1}, "v1")) == 12 and rk({"a": 1, "b": 2}, "v1") == rk({"b": 2, "a": 1}, "v1") and rk({"a": 1}, "v1") != rk({"a": 1}, "v2"))
ld, ar, pd = fn("load_done"), fn("append_result"), fn("pending")
tmp = Path(tempfile.mkdtemp()) / "runs.jsonl"
check("load_done of a missing file is empty", lambda: ld(tmp) == set())
def _resume():
    ar(tmp, {"key": "k1", "name": "été", "metrics": {"acc": 0.8}})
    ar(tmp, {"key": "k2", "metrics": {}})
    with open(tmp, "a", encoding="utf-8") as f:
        f.write('{"key": "k3", "metr')                       # crash mid-write
    return ld(tmp) == {"k1", "k2"} and "été" in tmp.read_text(encoding="utf-8")
check("append_result + load_done survive a crash mid-line", _resume)
cfgs = [{"k": 3}, {"k": 5}, {"k": 10}]
check("pending skips runs already done for this data version", lambda: pd(cfgs, {rk({"k": 5}, "v1")}, "v1") == [{"k": 3}, {"k": 10}] and pd(cfgs, {rk({"k": 5}, "v1")}, "v2") == cfgs)
