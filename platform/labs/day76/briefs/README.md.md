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

## Your mission
Write the README of your project repository.

## Steps
1. Title, one sentence, CI badge.
2. What it does (user's view), Architecture (Mermaid), Quickstart (exact commands).
3. Configuration table from `settings.py`, Evaluation from `results.md`, Limitations.
4. Ask someone to follow your Quickstart on a fresh machine. Fix every step where they got stuck.

## Done when
**Check** passes and someone else got the project running from the README alone.
