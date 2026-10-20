# Cleanup that always runs
**Topic:** `with` guarantees cleanup, even when the block raises.

## Your mission
Write the same timer twice, as a class and as a generator, and prove cleanup survives errors.

## Steps
1. `Timer.__enter__`: save the start time, `return self`.
2. `Timer.__exit__`: set `self.elapsed`, print it, return `False`.
3. `timer`: wrap the `yield` in `try:` / `finally:` and print in `finally`.
4. **Run**: the "failing block" line must still print.

## Done when
**Check** confirms both versions print on success and on error, and let the error through.
