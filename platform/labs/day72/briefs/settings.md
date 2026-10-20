# Settings and secrets
**Topic:** typed configuration from environment variables and a .env file, every error at once, secrets redacted.

## Real example
A Flask-style app that crashes one missing variable at a time, versus reporting them all (different app, same pain):

```python
env = {"PORT": "eighty"}
needed = {"DB_URL": str, "PORT": int, "SECRET": str}
problems = []
for name, kind in needed.items():
    if name not in env:
        problems.append(f"{name} is required")
        continue
    try:
        kind(env[name])
    except ValueError:
        problems.append(f"{name}: invalid {kind.__name__} {env[name]!r}")
print("; ".join(problems))
```

One run shows all three problems. Deploying on the agency's PC, that's one fix-and-retry instead of three.

## Your mission
Replace every hard-coded URL, key and number in your project with settings.

## Steps
1. `parse_env_file` and `coerce`.
2. `load_settings` with precedence and collected errors.
3. `redacted` for logging.
4. Create `.env` next to this file, add `.env` to `.gitignore`, and commit a `.env.example` with fake values instead.

## Done when
**Check** passes and `git grep -n "sk-\|localhost:5432"` finds nothing in your project code.
