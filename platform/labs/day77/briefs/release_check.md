# Release check
**Topic:** before sharing the repository: required files present, local files ignored, no secrets, no huge files.

## Real example
How fast a leaked key is found, and why a regex scan before pushing is worth it (any repository):

```python
import re
diff = '''+ client = Anthropic(api_key="sk-ant-api03-Xy7Q9mZ2bT4kL8pR1vW6nC3d")
+ DB_URL = os.environ["DATABASE_URL"]'''
for n, line in enumerate(diff.splitlines(), 1):
    if re.search(r"sk-ant-[A-Za-z0-9_-]{20,}", line):
        print(f"line {n}: API key in the diff, do NOT push. Revoke it if it was ever pushed.")
```

Bots scan public GitHub pushes continuously. A key pushed once must be revoked, even if you delete it in the next commit: it stays in the history.

## Your mission
A script you run before sending the repository link to Anis or a recruiter.

## Steps
1. `missing_files`, `ignored`.
2. `find_secrets` with the patterns (placeholders and `${VAR}` references must not trigger).
3. `scan` (skip `.git` and virtual environments) and `release_ok`.
4. **Run** `python release_check.py <your project folder>`. Fix everything until it prints READY TO SHARE.

## Done when
**Check** passes and your project prints READY TO SHARE.
