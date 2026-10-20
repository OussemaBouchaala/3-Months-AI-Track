# The code under test
**Topic:** the project's core functions in one module, read before testing them.

## Real example
In your project repository these live in `app/core.py`, and tests import them by name:

```python
import math
def percentile(values, p):
    s = sorted(values)
    return s[max(1, math.ceil(p / 100 * len(s))) - 1] if s else None
print(percentile([3, 1, 2], 50), percentile([], 95))
```

## Your mission
Read `core.py`. Don't change it: today's lab is `test_core.py`.

## Steps
1. Open this file once so Bench saves it next to `test_core.py`.
2. For each function, write down one behavior that would hurt the agency if it broke.
