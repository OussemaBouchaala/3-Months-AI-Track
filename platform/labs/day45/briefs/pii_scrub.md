# Mask personal data
**Topic:** detect phones, IDs, emails and bank numbers with regex, mask them consistently, and put them back only where it's safe.

## Real example
Masking order numbers in support tickets (a different kind of ID, same idea):

```python
import re
mapping, reverse = {}, {}
def mask(m):
    v = m.group()
    if v not in reverse:
        reverse[v] = f"[ORDER_{len(reverse) + 1}]"
        mapping[reverse[v]] = v
    return reverse[v]
t = re.sub(r"\bCMD-\d{6}\b", mask, "CMD-123456 late, CMD-777777 ok, CMD-123456 again")
print(t)
print(mapping)
```

`re.sub` accepts a function: perfect for numbered placeholders that stay consistent.

## Your mission
Write the scrubber you'll run on every real document before indexing it or sending it to an API.

## Steps
1. Write `PHONE` and `CIN` regexes. `(?<!\d)` and `(?!\d)` stop a match inside a longer number.
2. `find_pii`: patterns in order, drop overlapping matches.
3. `scrub` with a shared `mapping`, then `scrub_names` for known names.
4. `restore` for display on the agent's side only.
5. **Run** on 5 real messages from your interview; note what slips through.

## Done when
**Check** passes and the real messages come out without a phone, CIN or email.
