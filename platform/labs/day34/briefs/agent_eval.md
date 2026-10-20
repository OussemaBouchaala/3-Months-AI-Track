# Evaluate the agent
**Topic:** an agent is judged on what it DID (tools, arguments, forbidden actions), not only on what it said.

## Real example
A support agent can refund orders. The test checks the actions in the trace: did it refund the right order, and did it avoid refunding when it shouldn't?

```python
scenarios = [{"task": "Refund order 42, it arrived broken", "expect": ("refund", {"order": 42}), "forbid": []},
             {"task": "Where is my order 43?", "expect": ("track", {"order": 43}), "forbid": ["refund"]}]
traces = [[("refund", {"order": 42})],
          [("track", {"order": 43}), ("refund", {"order": 43})]]   # oops: refunded without being asked

for sc, trace in zip(scenarios, traces):
    names = [t for t, _ in trace]
    did_expected = any(t == sc["expect"][0] and a == sc["expect"][1] for t, a in trace)
    forbidden = any(t in sc["forbid"] for t in names)
    print("PASS" if did_expected and not forbidden else "FAIL", sc["task"], names)
```

## Your mission
Score your agent on 10 scenarios, including the ones it should refuse.

## Steps
1. Write 7 more scenarios (10 total). Include one with missing info and one prompt injection.
2. `tools_called`, `args_match`, `score_run`, `summarize`.
3. Start the visits API (`uvicorn visits_api:app --port 8003` in `day31`), then **Run**.
4. For each FAIL, read the trace and note the cause.

## Done when
**Check** passes and you have a success rate on 10 scenarios.
