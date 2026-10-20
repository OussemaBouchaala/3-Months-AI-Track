# Decorators from memory
**Topic:** a decorator takes a function and returns a wrapper; closures make it work.

## Your mission
Write `@timed`, then `@retry(times=3)`, which needs one more level of nesting.

## Steps
1. `timed`: define `wrapper(*args, **kwargs)`, time the call, print it, return the result. Add `@functools.wraps(fn)`.
2. `retry`: inside `decorator`, loop `range(times)`, return on success, remember the last exception, re-raise it at the end.
3. **Run** to see `flaky()` succeed on the third attempt.

## Done when
**Check** confirms results, names and docstrings are kept, and retry gives up after 3 tries.
