"""Week 11: Ship (Dec 14-20, 2026)."""
from lab_files import lab

DAY71 = {
    "id": "w11d1", "folder": "day71", "date": "2026-12-14", "weekday": "Mon",
    "title": "Tests that catch bugs", "minutes": 75,
    "why": "This week the project leaves your laptop. Tests are what let you (or anyone) change it later without breaking the agency's tool.",
    "lesson": r"""
:::hook
You have 12 tests, all green. Someone "simplifies" the phone regex and drops the lookarounds. CINs get masked as phones, 9-digit references get cut in half. All 12 tests still pass: none of them tried a CIN. Green tests that can't fail are decoration.
:::

## One behavior per test

```python
def percentile(values, p):
    import math
    s = sorted(values)
    return s[max(1, math.ceil(p / 100 * len(s))) - 1] if s else None

def test_p95_of_1_to_20():
    assert percentile(list(range(1, 21)), 95) == 19

def test_empty_is_none():
    assert percentile([], 95) is None

test_p95_of_1_to_20(); test_empty_is_none(); print("2 passed")
```

Small tests with clear names tell you **what** broke when one fails. `test_everything` tells you nothing.

## Test the edges

The bugs live at boundaries: empty input, exactly max_chars, the first digit 0 vs 2, `[0]` as a citation, an Arabic letter with a diacritic. For each function, ask "what input would a lazy implementation get wrong?"

:::analogy
A fire drill that only checks the doors open. Useful, but nobody tested the stairs with smoke. Tests should simulate the failures you fear, not the day everything is fine.
:::

## Mutation testing

Plant a bug (a **mutant**): remove the alef rule, use `round` instead of `ceil`, drop the lookbehind. Run the tests. If they still pass, the mutant **survived**, and you've found a missing test. Bench's check plants 8 mutants; tools like `mutmut` do it automatically on real projects.

:::predict Your coverage report says 100% of core.py lines run during tests. Can a mutant still survive?
---
Yes. Coverage says the line ran, not that any assertion checked its result. A test that calls `mask_phones("x")` covers the regex and asserts nothing useful about CINs.
:::

:::check
? Which test kills the "round instead of ceil" percentile mutant?
- percentile([5], 50) == 5
* percentile(list(range(1, 21)), 95) == 19
- percentile([], 95) is None
- percentile([1, 2], 100) == 2
> The others give the same answer with both formulas. Kill mutants with inputs where the formulas disagree.
:::

:::mistake
Tests that call the model or the database. They're slow, flaky and cost money. Core logic gets pure unit tests; the service gets tests with fake retrieve/generate (Week 8's injection pays off here).
:::

:::cards
One test checks? :: One behavior, with a name that says which.
Where do bugs hide? :: Boundaries and edge cases.
Mutant? :: A deliberately planted bug.
Survived mutant? :: A missing test.
Coverage vs mutation score? :: Lines run vs bugs caught.
:::

:::explain Explain mutation testing to a classmate with the phone regex example.
:::
""",
    "files": [
        lab("day71", "core.py"),
        lab("day71", "test_core.py", task=[0, 1]),
    ],
    "tasks": [
        "test_core.py: 9+ focused tests for the core functions",
        "Kill all 8 planted mutants; run pytest from the terminal",
        "Move the tests into your project repo (tests/) and run them there",
    ],
    "done_when": "All tests green on the real code, no surviving mutant, and pytest runs in the project repo.",
    "resources": [{"label": "pytest: getting started", "url": "https://docs.pytest.org/en/stable/getting-started.html"},
                  {"label": "mutmut (mutation testing)", "url": "https://mutmut.readthedocs.io/"}],
    "quiz": [
        {"q": "A mutant survives. That means...", "options": ["The code is correct", "No test detects that bug", "The test crashed", "Coverage is low"], "answer": 1,
         "explain": "Add a test where the mutant and the real code disagree."},
        {"q": "Unit tests for core functions should call...", "options": ["The real model", "Only the pure functions, no network", "The production database", "The UI"], "answer": 1,
         "explain": "Fast, deterministic, free."},
    ],
}

DAY72 = {
    "id": "w11d2", "folder": "day72", "notes_task": 2, "date": "2026-12-15", "weekday": "Tue",
    "title": "Settings and secrets", "minutes": 75,
    "why": "The agency's PC isn't your laptop. Every hard-coded URL, port and key is a failed deployment, or a leaked secret.",
    "lesson": r"""
:::hook
You install the project on the agency's PC. It crashes: "connection refused localhost:5432". You fix it, restart: crash, missing API key. Fix, restart: crash, TOP_K is "five". Three trips for three errors that one run could have listed together.
:::

## Twelve-factor style config

Configuration lives in **environment variables**, read in one place, typed, with defaults:
- Real environment (Docker, the server) wins.
- A `.env` file for local development (never committed).
- Defaults in code for everything that isn't secret or machine-specific.

```python
import os
env = {"TOP_K": "8", "RERANK": "yes"}
def as_bool(v): return v.strip().lower() in ("1", "true", "yes", "on")
settings = {"TOP_K": int(env.get("TOP_K", "5")), "RERANK": as_bool(env.get("RERANK", "true")),
            "OLLAMA_URL": env.get("OLLAMA_URL", "http://localhost:11434")}
print(settings)
```

:::analogy
A rental car: the car (your code) is the same for everyone; each driver adjusts the seat and mirrors (settings) for their body. Nobody welds the seat in place for one driver.
:::

## Fail fast, all at once

At startup, validate everything and report every problem in one message. A service that starts with a bad setting fails later, at 10:42, in front of a client.

## Secrets

- `.env` in `.gitignore`, `.env.example` (fake values) committed.
- Never log a secret: redact it (`***f00d`).
- In CI and production: the platform's secret store, not files.

:::predict Your `.env` was committed last month, then deleted. Is the key safe now?
---
No. It's in the git history forever (and maybe already scraped). Revoke the key and create a new one; deleting the file doesn't undo a push.
:::

:::check
? Which belongs in a default value in code?
- The API key
- The database password
* TOP_K = 5
- The agency's server IP
> Defaults for tuning knobs; secrets and machine addresses come from the environment.
:::

:::mistake
`bool(os.environ.get("RERANK"))`: the string "false" is truthy, so `RERANK=false` turns reranking ON. Parse booleans explicitly.
:::

:::cards
Precedence? :: Environment > .env file > default.
.env in git? :: Never; commit .env.example.
Startup validation? :: Report all problems at once, then refuse to start.
bool("false")? :: True: parse booleans explicitly.
Logging settings? :: Redact secrets first.
:::

:::explain Explain why the API key is not in the code or the compose file.
:::
""",
    "files": [
        lab("day72", "settings.py", task=[0, 1]),
    ],
    "tasks": [
        "settings.py: parse_env_file, coerce with strict booleans",
        "load_settings with precedence and all errors at once; redacted",
        "Replace hard-coded values in your project; add .env.example and .gitignore",
    ],
    "done_when": "No URL, key or tuning number is hard-coded in the project; a bad .env lists every problem at once.",
    "resources": [{"label": "The Twelve-Factor App: config", "url": "https://12factor.net/config"}],
    "quiz": [
        {"q": "RERANK=false and the code does bool(os.environ['RERANK']). Result?", "options": ["False", "True", "Error", "None"], "answer": 1,
         "explain": "Any non-empty string is truthy."},
        {"q": "A key was pushed then deleted. You should...", "options": ["Nothing", "Revoke and replace it", "Rewrite history only", "Make the repo private only"], "answer": 1,
         "explain": "Assume it's compromised."},
    ],
}

DAY73 = {
    "id": "w11d3", "folder": "day73", "date": "2026-12-16", "weekday": "Wed",
    "title": "Logs and metrics", "minutes": 75,
    "why": "Once it runs at the agency, you can't watch it. Logs and metrics are how you find out what happened when you weren't there.",
    "lesson": r"""
:::hook
Salma calls: "this morning it was slow and gave a weird answer about a contract". Without logs: you guess. With one JSON line per request: you search the morning's lines, find the 14-second one, see the retrieval took 12 s (the database was re-indexing), and the answer cited a chunk from the old contract version.
:::

## One structured line per request

```python
import json
line = {"ts": "2026-12-16T09:42:10+00:00", "request_id": "a1b2", "question": "caution ? [PHONE]",
        "stage_ms": {"retrieve": 12040, "generate": 1900}, "total_ms": 13940, "status": "ok"}
print(json.dumps(line, ensure_ascii=False))
```

JSON, not prose: you can filter by request id, sort by total_ms, count statuses, with three lines of Python or `jq`.

:::analogy
A flight data recorder: it doesn't prevent crashes, but after one, investigators know exactly what happened in each second. Nobody reconstructs a crash from the pilot's memory.
:::

## Time each stage

`retrieve`, `rerank`, `generate`, `citations`. The total says "slow"; the stages say **where**. A context manager records the time even when the stage raises.

## Metrics

Counters (requests, errors, IDK answers) and latency histograms (p50, p95). Expose them at `GET /metrics`. A daily glance shows trends before users complain.

## Never log personal data

The question is redacted before logging. A log file is copied, emailed, uploaded to support tickets; it's the most common place PII leaks.

:::predict Logs show p95 total = 9 s, p95 retrieve = 7 s. Where do you look first?
---
Retrieval: the database (missing HNSW index? re-indexing during work hours?) or the embedding call. Optimizing the prompt won't help; it's 2 seconds of the 9.
:::

:::check
? Why include the request id in every log line?
- To make lines longer
* To connect a user's report, the response header and every log line of that request
- For sorting
- JSON requires it
> The thread that ties everything together.
:::

:::mistake
`print()` debugging left in production: unstructured, no timestamps, no levels, and often the full question with the client's phone number.
:::

:::cards
Log format? :: One JSON object per line.
Stage timings? :: Show where the time goes, not just that it's slow.
timed() on exceptions? :: Still records the duration.
Metrics endpoint? :: Counters and p50/p95 per stage.
PII in logs? :: Redact before writing.
:::

:::explain Explain how you'd investigate "it was slow this morning" with your logs.
:::
""",
    "files": [
        lab("day73", "observability.py", task=[0, 1]),
    ],
    "tasks": [
        "observability.py: redact, JsonFormatter, timed",
        "Metrics.snapshot and log_request; /metrics in your service",
        "Make 10 requests, then find the slowest one in requests.log by its request id",
    ],
    "done_when": "Every request writes one redacted JSON line with stage timings, and /metrics shows p95 per stage.",
    "resources": [{"label": "Python logging cookbook", "url": "https://docs.python.org/3/howto/logging-cookbook.html"}],
    "quiz": [
        {"q": "Total p95 9 s, retrieve p95 7 s. First suspect?", "options": ["The prompt", "Retrieval / database", "The UI", "The network to the client"], "answer": 1,
         "explain": "Stage timings point at the slow part."},
        {"q": "Why JSON lines instead of text logs?", "options": ["Prettier", "Filterable and countable by field", "Smaller", "Required by Python"], "answer": 1,
         "explain": "Machines can query them."},
    ],
}

DAY74 = {
    "id": "w11d4", "folder": "day74", "notes_task": 2, "date": "2026-12-17", "weekday": "Thu",
    "title": "One-command deployment", "minutes": 75,
    "why": "\"docker compose up\" is the difference between \"come to my laptop\" and \"it runs at the agency\".",
    "lesson": r"""
:::hook
Installing on the agency's PC by hand: Python version, Postgres, pgvector extension, Ollama, the models, environment variables, the right start order. Two hours and a page of notes, and next time you'll forget step 6. A compose file is that page of notes, executable.
:::

## Three services

| service | image | needs |
|---|---|---|
| db | pgvector/pgvector:pg16 | a data volume, a health check |
| ollama | ollama/ollama | a models volume |
| api | built from your Dockerfile | db healthy, env file, port 8000 |

Services reach each other **by name**: the API connects to `db:5432` and `http://ollama:11434`. `localhost` inside a container is the container itself.

```python
inside_api = {"DATABASE_URL": "postgresql://postgres:***@db:5432/rag", "OLLAMA_URL": "http://ollama:11434"}
for k, v in inside_api.items():
    print(k, "->", "OK" if "localhost" not in v else "WRONG: localhost is the api container itself")
```

:::analogy
An apartment building's intercom: you buzz "flat 3B", not a street address. Inside the compose network, service names are the flat numbers.
:::

## Start order that actually works

`depends_on: [db]` waits for the container to **start**, not for Postgres to **accept connections**. Add a health check (`pg_isready`) to db and `condition: service_healthy` to the API.

## Data that survives

Named volumes for the database and the models. Without them, `docker compose down` deletes the index and the 2 GB of models.

:::predict You run `docker compose down -v`. What happens to the index?
---
`-v` deletes the named volumes: the index and the downloaded models are gone. Plain `down` keeps them. Know the difference before running it at the agency.
:::

:::check
? The API logs "connection refused localhost:5432" inside compose. Fix?
- Open port 5432 on the host
* Use the service name: db:5432
- Restart Docker
- Use 127.0.0.1
> localhost is the API's own container.
:::

:::mistake
Secrets in `docker-compose.yml` (`LLM_API_KEY: sk-...`). The compose file is committed. Use `env_file: .env` and keep `.env` out of git.
:::

:::cards
Service-to-service address? :: The service name (db, ollama).
depends_on alone waits for? :: Container start, not readiness.
Wait for readiness? :: healthcheck + condition: service_healthy.
Keep data across restarts? :: Named volumes.
down -v? :: Deletes the volumes: index and models gone.
:::

:::explain Explain what happens, in order, when you run docker compose up -d on a fresh machine.
:::
""",
    "files": [
        lab("day74", "docker-compose.yml", task=[0, 1]),
    ],
    "tasks": [
        "docker-compose.yml: db with health check and volume, ollama with volume",
        "api: build, env_file, service-name URLs, depends_on healthy, restart, health check",
        "docker compose up -d --build on your machine; run the smoke test against it",
    ],
    "done_when": "docker compose ps shows all services healthy and the smoke test passes.",
    "resources": [{"label": "Compose: startup order", "url": "https://docs.docker.com/compose/how-tos/startup-order/"},
                  {"label": "Compose file reference", "url": "https://docs.docker.com/reference/compose-file/"}],
    "quiz": [
        {"q": "Inside compose, the API reaches Postgres at...", "options": ["localhost:5432", "db:5432", "127.0.0.1:5432", "host.docker.internal only"], "answer": 1,
         "explain": "Service names are hostnames on the compose network."},
        {"q": "What does condition: service_healthy add?", "options": ["Nothing", "Waits for the health check to pass, not just the container start", "Restarts on failure", "Opens ports"], "answer": 1,
         "explain": "Postgres needs a few seconds after start."},
    ],
}

DAY75 = {
    "id": "w11d5", "folder": "day75", "date": "2026-12-18", "weekday": "Fri",
    "title": "Continuous integration", "minutes": 75,
    "why": "CI runs your tests on every push, on a clean machine. It catches the \"works on my laptop\" bugs before anyone else sees them.",
    "lesson": r"""
:::hook
You push a fix at 23:00. It imports a package you installed locally but never added to requirements.txt. On your laptop: fine. On the agency's PC next week: crash at startup. CI would have failed within 3 minutes of the push, on a fresh machine, with a red ✗ on the commit.
:::

## The workflow

```python
pipeline = ["checkout", "setup Python 3.12 (pip cache)", "pip install -r requirements.txt", "ruff check .",
            "pytest -q", "docker build"]
for i, step in enumerate(pipeline, 1):
    print(i, step)
```

Triggers: every push to main and every pull request. Each step must succeed (exit code 0) for the next to run.

:::analogy
The quality check at the end of a bakery line: every loaf passes the same scale and the same look before going on the shelf. Nobody skips it because "this batch looks fine".
:::

## What CI proves

- The dependencies in requirements.txt are enough (fresh machine).
- The code passes the linter (unused imports, undefined names).
- The tests pass, including the mutation-hardened ones from Monday.
- The Docker image builds.

## Green or nothing

A red CI that people ignore is worse than none: it trains everyone to ignore it. Fix or revert immediately. Never `pytest || true` to make it green.

:::predict Tests pass locally and fail in CI with "ModuleNotFoundError: No module named 'pypdf'". Why?
---
pypdf is installed on your laptop but missing from requirements.txt. CI starts from a clean machine, so it only has what the file lists. Add it; that's exactly the bug CI exists to catch.
:::

:::check
? Why cache pip in setup-python?
- Security
* Faster runs: dependencies aren't downloaded again on every push
- It's required
- To use older versions
> Same result, a minute faster per run.
:::

:::mistake
Putting an API key in the workflow file. Tests should use fakes; if a step really needs a key, use the repository's Secrets settings (`${{ secrets.NAME }}`).
:::

:::cards
CI triggers? :: Push to main and pull requests.
Steps? :: Checkout, setup-python, install, lint, test, build.
Fails only in CI? :: Usually a missing dependency or a local-only file.
Red CI? :: Fix or revert now; never silence it.
Secrets in CI? :: Repository secrets, never in the YAML.
:::

:::explain Explain what the green badge on your README guarantees, and what it doesn't.
:::
""",
    "files": [
        lab("day75", "ci.yml", task=[0, 1]),
    ],
    "tasks": [
        "ci.yml: triggers, setup-python with cache, install, ruff, pytest",
        "docker job with needs: test; push it to your project repo",
        "Get the Actions run green; break a test on purpose once and watch it go red",
    ],
    "done_when": "The project's Actions tab shows a green run and the badge works.",
    "resources": [{"label": "GitHub Actions: building and testing Python", "url": "https://docs.github.com/en/actions/use-cases-and-examples/building-and-testing/building-and-testing-python"},
                  {"label": "Ruff", "url": "https://docs.astral.sh/ruff/"}],
    "quiz": [
        {"q": "Tests pass locally, fail in CI with ModuleNotFoundError. Cause?", "options": ["GitHub bug", "A dependency missing from requirements.txt", "Slow runner", "Wrong branch"], "answer": 1,
         "explain": "CI only installs what you list."},
        {"q": "Making CI green with `pytest || true` is...", "options": ["Fine for now", "Hiding failures; never do it", "Faster", "Required for Docker"], "answer": 1,
         "explain": "A gate that always opens isn't a gate."},
    ],
}

DAY76 = {
    "id": "w11d6", "folder": "day76", "date": "2026-12-19", "weekday": "Sat",
    "title": "The README", "minutes": 180,
    "why": "Recruiters spend 30 seconds on a repository. Anis will forward the link. The README decides whether anyone looks further.",
    "lesson": r"""
:::hook
Two repositories with the same code. One README says "RAG project. Run main.py." The other opens with what it does for whom, a green CI badge, a diagram, three commands that start it, and a results table with intervals. Only one of them gets an interview.
:::

## What a reader needs, in order

1. **What is it?** One sentence, for whom.
2. **Does it build?** The CI badge.
3. **What does it do?** Bullets from the user's view.
4. **How does it work?** The Mermaid diagram.
5. **How do I run it?** Exact commands, copy-paste.
6. **What can I configure?** A table of variables.
7. **How well does it work?** The results table with intervals.
8. **What doesn't it do?** Limitations.

```python
sections = ["What it does", "Architecture", "Quickstart", "Configuration", "Evaluation", "Limitations"]
readme = "# Dar Assistant\n" + "\n".join(f"## {s}\n..." for s in sections)
print(readme.count("## "), "sections:", ", ".join(sections))
```

:::analogy
A restaurant's front window: the menu with prices, the hours, a photo of the dining room. Nobody walks in to find out whether it's open.
:::

## Quickstart is a test

The Quickstart must work, word for word, on a fresh machine. Give it to someone (a friend, a classmate) with no help. Every place they get stuck is a bug in your README.

:::predict Your Quickstart says "set up the database". What happens when a recruiter tries it?
---
They stop. Vague steps are where readers quit. Write the exact commands: `cp .env.example .env`, `docker compose up -d --build`, the model pull, the indexing command, the URL to open.
:::

:::check
? Which belongs at the very top of the README?
- The license
- The folder structure
* One sentence on what it does and for whom, plus the CI badge
- The changelog
> Answer "what is this?" in five seconds.
:::

:::mistake
Results without the test set size or intervals ("94% accuracy!"). An experienced reader assumes it's on training data. "0.86 [0.74, 0.95] on 42 held-out questions" is credible.
:::

:::cards
README first line? :: What it does, for whom.
Badge? :: CI status, proves it builds.
Quickstart? :: Exact commands, tested on a fresh machine.
Configuration? :: Table of variables with defaults.
Results? :: With intervals and test set size.
:::

:::explain Walk through your README as if you were a recruiter seeing it for the first time.
:::
""",
    "files": [
        lab("day76", "README.md", task=[0, 1]),
    ],
    "tasks": [
        "README.md: title, badge, what it does, architecture, quickstart",
        "Configuration table, evaluation with intervals, limitations",
        "Have someone follow the Quickstart on a fresh machine; fix every snag",
    ],
    "done_when": "Someone else started the project from the README alone.",
    "resources": [{"label": "Make a README", "url": "https://www.makeareadme.com/"},
                  {"label": "GitHub: Mermaid in Markdown", "url": "https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams"}],
    "quiz": [
        {"q": "Best evidence that the project works, in a README?", "options": ["'Works great!'", "A results table with intervals on held-out questions", "Many stars", "A long feature list"], "answer": 1,
         "explain": "Numbers with context."},
        {"q": "How do you test a Quickstart?", "options": ["Read it twice", "Someone follows it on a fresh machine", "Run it on your laptop", "Ask ChatGPT"], "answer": 1,
         "explain": "Your machine has everything already installed."},
    ],
}

DAY77 = {
    "id": "w11d7", "folder": "day77", "retest_task": 1, "date": "2026-12-20", "weekday": "Sun",
    "title": "Release check", "minutes": 150,
    "why": "Next week you send this link to people. One leaked key or a missing file undoes six weeks of good work.",
    "lesson": r"""
:::hook
Bots scan every public push to GitHub for API keys. A student pushes a repo with an `sk-ant-...` key in a test file at 22:10; by 22:13 the key is being used to run someone else's workloads on their bill. Deleting the file at 22:20 doesn't help: the key is in the history.
:::

## Before sharing, check four things

1. **Required files**: README, requirements, Dockerfile, compose, `.env.example`, `.gitignore`, CI workflow.
2. **Ignored files**: `.env`, the feedback database, logs, `__pycache__`.
3. **No secrets** in tracked files: API keys, AWS keys, private keys, quoted passwords.
4. **No huge files**: model weights, dumps, datasets belong elsewhere.

```python
import re
line = 'client = Anthropic(api_key="sk-ant-api03-Xy7Q9mZ2bT4kL8pR1vW6nC3d")'
print("secret found" if re.search(r"sk-ant-[A-Za-z0-9_-]{20,}", line) else "clean")
print("placeholder ok" if not re.search(r"sk-ant-[A-Za-z0-9_-]{20,}", "LLM_API_KEY=") else "?")
```

:::analogy
Checking your pockets before going through airport security: keys, phone, the knife you forgot was in your bag. Thirty seconds before is much cheaper than the conversation after.
:::

## If a key leaked

1. **Revoke it** in the provider's console, now.
2. Create a new one, put it in `.env`.
3. Then clean the history if you want, but the revocation is what protects you.

:::predict The scanner flags your local `.env` with a real key. Is the release blocked?
---
No, if `.gitignore` covers `.env` and it's not tracked: that's where the key is supposed to live. The release check allows secrets only there. A key anywhere else blocks the release.
:::

:::check
? You find a key in a commit from last week. First action?
- Delete the file and push
- Rewrite the git history
* Revoke the key in the provider's console
- Make the repository private
> Assume it's already copied; only revocation makes it useless.
:::

:::mistake
Committing a 2 GB model or a dataset "to make it easy to run". The repo becomes unclonable, and GitHub rejects files over 100 MB anyway. Document how to download them instead.
:::

:::cards
Required files? :: README, requirements, Dockerfile, compose, .env.example, .gitignore, CI.
Allowed place for real secrets? :: The local, git-ignored .env.
Leaked key, first step? :: Revoke it.
Placeholder vs secret? :: Empty or ${VAR} references are fine; literal keys aren't.
Large files? :: Not in git; document the download.
:::

:::explain Explain to a classmate what they should check before making their project repository public.
:::
""",
    "files": [
        lab("day77", "release_check.py", task=0),
    ],
    "tasks": [
        "release_check.py: READY TO SHARE on your project",
        "Beat the Week 11 boss (8/10)",
        "Retro in notes; tag the release (git tag v1.0) and push",
    ],
    "done_when": "Your project prints READY TO SHARE, is tagged v1.0, and you got 8/10 on the boss.",
    "resources": [{"label": "GitHub: removing sensitive data", "url": "https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository"}],
    "quiz": [
        {"q": "A key was pushed. Most important step?", "options": ["Delete the file", "Revoke the key", "Rename the repo", "Squash commits"], "answer": 1,
         "explain": "History and scrapers keep copies."},
    ],
    "retest": [
        {"q": "A mutant survives your tests. You should...", "options": ["Delete the mutant", "Add a test where it and the real code disagree", "Raise coverage", "Ignore it"], "answer": 1,
         "explain": "It's a missing test."},
        {"q": "100% line coverage guarantees...", "options": ["No bugs", "Every line ran, not that results were checked", "Mutation score 100%", "Fast tests"], "answer": 1,
         "explain": "Coverage ≠ assertions."},
        {"q": "bool('false') in Python is...", "options": ["False", "True", "None", "Error"], "answer": 1,
         "explain": "Non-empty strings are truthy."},
        {"q": "Settings precedence?", "options": ["Default > .env > environment", "Environment > .env > default", ".env > environment > default", "Random"], "answer": 1,
         "explain": "The real environment wins."},
        {"q": "Why one JSON log line per request?", "options": ["Shorter", "Filter and count by field, find a request by id", "Required", "Faster disk"], "answer": 1,
         "explain": "Logs you can query."},
        {"q": "Inside compose, the API reaches the database at...", "options": ["localhost", "db (the service name)", "the host IP", "0.0.0.0"], "answer": 1,
         "explain": "localhost is the container itself."},
        {"q": "depends_on without a condition waits for...", "options": ["Postgres to be ready", "The container to start", "The health check", "Nothing"], "answer": 1,
         "explain": "Add condition: service_healthy."},
        {"q": "docker compose down -v...", "options": ["Stops containers only", "Also deletes named volumes (index, models)", "Rebuilds images", "Shows logs"], "answer": 1,
         "explain": "Careful at the agency."},
        {"q": "CI fails with ModuleNotFoundError but local works. Fix?", "options": ["Retry CI", "Add the package to requirements.txt", "Disable the test", "Use || true"], "answer": 1,
         "explain": "CI starts clean."},
        {"q": "Where may a real API key live?", "options": ["In the README", "In the git-ignored local .env", "In ci.yml", "In docker-compose.yml"], "answer": 1,
         "explain": "Never in tracked files."},
    ],
}

WEEK11 = {
    "n": 11, "phase": "Phase 2", "title": "Ship", "dates": "Dec 14-20",
    "goal": "Deployable, documented, tested.",
    "gate": "One-command run",
    "days": [DAY71, DAY72, DAY73, DAY74, DAY75, DAY76, DAY77],
}
