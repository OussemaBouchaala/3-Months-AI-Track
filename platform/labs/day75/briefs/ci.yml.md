# Continuous integration
**Topic:** a GitHub Actions workflow: lint, test, build on every push, so a broken change can't reach the agency.

## Real example
What CI does, as a script (any project, same gate):

```python
import subprocess, sys
py = sys.executable
steps = [[py, "-c", "print('lint ok')"], [py, "-c", "print('tests ok')"], [py, "-c", "import sys; sys.exit(1)"]]
for cmd in steps:
    code = subprocess.run(cmd).returncode
    if code != 0:
        print("step failed:", cmd[-1], "-> stop, nothing is deployed")
        break
```

Each step's exit code decides whether the next one runs. That's why your smoke test returns 1 on failure.

## Your mission
Add CI to your project repository.

## Steps
1. Triggers: push to main, pull requests.
2. The test job: checkout, setup-python with cache, install, `ruff check .`, `python -m pytest -q`.
3. The docker job with `needs: test`.
4. Copy it to `.github/workflows/ci.yml` in your project, push, and watch the Actions tab. Fix until green.

## Done when
**Check** passes and the badge on your repository is green.
