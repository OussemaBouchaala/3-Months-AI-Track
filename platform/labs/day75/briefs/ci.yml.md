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

## How to read this file
The file in the editor is a complete GitHub Actions workflow. Read it top to bottom; the comments explain each part:

1. **`on:`**: when it runs (pushes to main, pull requests).
2. **The `test` job**: checkout, Python with a pip cache, install, `ruff check .`, `python -m pytest -q`. Each step's exit code decides whether the next one runs.
3. **The `docker` job** with `needs: test`: the image is only built when the tests pass.

## See it working
Copy it to `.github/workflows/ci.yml` in your project repository, push, and open the **Actions** tab on GitHub. A green run means lint, tests and build all passed; a red one shows which step failed.

Press **Check** under the editor to see the rules a useful CI workflow follows.
