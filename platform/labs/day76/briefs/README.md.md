# The README
**Topic:** the page a recruiter, a reviewer and the agency's next developer all read first.

## Real example
What a reader checks in 30 seconds, as a checklist (any project):

```python
readme = """# Parking finder
Finds free parking spots in Tunis from camera feeds. ![CI](https://github.com/x/y/actions/workflows/ci.yml/badge.svg)
## Quickstart
docker compose up -d
## Evaluation
Spot detection F1 0.91 [0.88, 0.94] on 400 test images."""
for question, ok in [("What is it?", readme.split("\n")[1] != ""), ("Does it build?", "badge.svg" in readme),
                     ("Can I run it?", "docker compose up" in readme), ("Does it work?", "[" in readme.split("Evaluation")[1])]:
    print(f"{question:15} {'yes' if ok else 'NO'}")
```

Four questions, answered in the first screen: what it is, whether it builds, how to run it, how well it works.

## How to read this example
An example README for the project repository. Notice how it's built:

1. **Title, one sentence and the CI badge**: what a recruiter sees in 5 seconds.
2. **What it does** from the user's point of view, then the **architecture** diagram.
3. **Quickstart**: exact commands that work on a fresh machine.
4. **Configuration** (from `settings.py`), **Evaluation** (from `results.md`) and honest **Limitations**.

Press **Check** under the editor to see the rules a good version follows. When you write your own, keep this structure and use your real numbers.
