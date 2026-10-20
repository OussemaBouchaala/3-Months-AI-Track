# The experiment grid
**Topic:** expand configurations, drop the pointless ones, give each run a stable key, and resume after a crash.

## Real example
A bakery testing recipes: flour x hydration x proofing time (different experiments, same bookkeeping):

```python
import itertools, hashlib, json
space = {"flour": ["T55", "T65"], "hydration": [0.65, 0.75], "proof_h": [2, 12]}
runs = [dict(zip(space, v)) for v in itertools.product(*space.values())]
runs = [r for r in runs if not (r["flour"] == "T55" and r["proof_h"] == 12)]   # known to fail
for r in runs[:3]:
    print(hashlib.sha1(json.dumps(r, sort_keys=True).encode()).hexdigest()[:8], r)
print(len(runs), "bakes")
```

If the oven breaks after bake 4, the keys tell you exactly which bakes are left.

## Your mission
Prepare Week 10's runs so they can be interrupted and resumed safely.

## Steps
1. `expand_grid`, `filter_valid` (add your own rules).
2. `config_name`, `run_key` (includes the data version).
3. `append_result`, `load_done` (tolerate a broken last line), `pending`.
4. Edit `SPACE` for your project; **Run** to see how many configs you'll evaluate. Cut it if it's more than you can run.

## Done when
**Check** passes and a second run after a stop only does the remaining configs.
