# The mutable default trap
**Topic:** a default value is created once, when `def` runs, and shared by every call.

## Your mission
Reproduce the bug, then fix it, first on a toy function and then on a realistic server helper.

## Steps
1. `add_buggy`: append `x` to `items` and return `items`. Keep `items=[]`.
2. `add_fixed`: same job, but default to `None` and build the list inside: `if items is None: items = []`.
3. `log_request_buggy` and `log_request`: the same pair for a request log.
4. Write your prediction for the `__main__` prints, press **Run**, compare.

## Done when
**Check** is all green: the buggy versions share one list, the fixed ones don't.
