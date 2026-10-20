# Tests that catch bugs
**Topic:** pytest-style tests for the core functions, judged by mutation testing: each planted bug must make a test fail.

## Real example
A test suite for a VAT function, and the bug it misses (a different function, the same lesson):

```python
def vat(price, rate=0.19):
    return round(price * (1 + rate), 3)

def buggy_vat(price, rate=0.19):
    return round(price * (1 + 0.19), 3)          # ignores the rate argument

def weak_test(f):
    return f(100) == 119.0                       # only the default rate

def strong_test(f):
    return f(100) == 119.0 and f(100, rate=0.07) == 107.0

print("weak catches the bug:", not weak_test(buggy_vat))
print("strong catches the bug:", not strong_test(buggy_vat))
```

Both tests pass on the real function. Only the strong one fails on the bug. Coverage counts lines; mutation testing counts bugs caught.

## Your mission
Write the tests your CI will run on every push next week.

## Steps
1. Open `core.py` once (so it's saved next to this file) and read it.
2. Write 9+ small tests, one behavior each, with plain `assert`.
3. **Check**: it plants 8 bugs; every one must make at least one test fail. If a bug survives, the check names it: add the missing test.
4. `pip install pytest`, then in a terminal: `python -m pytest test_core.py -q`.

## Done when
**Check** passes: all your tests pass on the real code and none survives a planted bug.
