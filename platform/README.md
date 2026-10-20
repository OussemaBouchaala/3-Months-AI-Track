# Bench

A local learning platform for your 12-week plan: lessons, a code editor, a Run button with output and plots, quizzes, notes, and progress tracking. Your code is saved as real files in `work/dayNN/`.

## Install (once)

Bench lives in `platform/` of the `ml-bench` folder; your code lives in `work/`:

```
ml-bench/
├── platform/    this app (lessons, labs, checks)
├── work/        your code: work/day01 ... work/day84
├── .venv/       created by setup.bat
├── setup.bat    creates .venv and installs requirements.txt
└── start.bat    starts Bench
```

Double-click `setup.bat` once (Mac/Linux: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`).

## Start

- **Windows:** double-click `start.bat` (in `ml-bench/` or `platform/`)
- **Mac/Linux:** `platform/start.sh`
- **Or:** with the venv active, `cd platform` then `python server.py`

Your browser opens at http://127.0.0.1:8766. Stop it with Ctrl+C in the terminal.

Bench runs your code with the Python it was started with, so start it from the `.venv` and every package installed there (scikit-learn, matplotlib, httpx...) is available.

## How a day works

Each week is an **arena** and each day a **level**. The header shows the arena (click it for the map of all arenas) and the path of its levels; the step bar below shows where you are in today's level. Play the steps in order, using the Next button at the bottom of each one:

1. **Learn:** read the lesson on the left. The code editor on the right is a scratchpad: press **Try it in the editor** on any example to run it there, or type your own experiments. Finish with "I've read the lesson".
2. **Practice:** one exercise at a time. The left side explains the topic, your mission and the steps; the editor on the right holds the starter, guided by comments. Write your prediction in the yellow box, **Run** (Ctrl+Enter) to compare it line by line with the real output, then **Check** (Ctrl+Shift+Enter) to see what's right and what's missing.
3. **Quiz:** answer from memory; the scratchpad stays open if you want to verify something.
4. **Boss** (Sundays): the week's re-test, 8/10 to win.
5. **Missions:** everything that clears the level. Passing labs, writing notes and beating the boss tick their missions for you; tick the rest (reading, GitHub, applications) yourself. Links marked ↗ open where you do them.

**Notes** (button in the step bar) open in a side drawer and save to `notes.md`. Each level has three stars: lesson read, every lab passing, perfect quiz. **Hide ›** folds the editor away when you want the guide wider.

Ctrl+S saves (it also autosaves). **Reset to starter** restores an exercise's original scaffold.

## AI: free models, the tutor, and your labs

Click **⚙ AI** in the header, pick a provider, paste its key, press **Save and test**. No terminal, no restart.

- **Google Gemini** (free key: https://aistudio.google.com/apikey)
- **Groq** (free key: https://console.groq.com/keys), open models, very fast
- **OpenRouter** (free key), pick a model ending in `:free`
- **Ollama** (https://ollama.com), open source models on your own computer, no key
- **Anthropic** (paid credits)

The key is saved in `bench/llm_settings.local.json` (git ignores it). **Ask AI** (bottom right) is a tutor that sees your lesson and code. Labs call the same model with:

```python
from bench_llm import get_client
client = get_client()   # same shape as anthropic.Anthropic()
```

## How lessons work

Lessons come one part at a time (**Continue**), with a real situation first, analogies, **Predict first** boxes (guess, then reveal), quick checks with instant feedback, flashcards, and an **Explain it in your own words** box the tutor gives feedback on. Every Python example has **Run ▶** to see its output in place. In Practice, each exercise starts with **a real example** of the same technique on a different problem, then your mission.

Lesson blocks are plain text in `curriculum.py`: `:::hook`, `:::analogy`, `:::predict <question>` (answer after `---`), `:::check` (`? question`, `- wrong`, `* right`, `> why`), `:::reveal <title>`, `:::key`, `:::mistake`, `:::cards` (`question :: answer` per line), `:::explain <prompt>`, each closed by `:::`. A brief's `## Real example` section is shown first.

## Exercises and checks

Each exercise starts as a scaffold: the imports, function names and signatures are written for you, and every `...` marks a part you fill in. Docstrings say what each function must return.

Starters and checks live in `labs/dayNN/`:

```
labs/day01/defaults.py           starter shown in the editor
labs/day01/briefs/defaults.md    the guided description shown beside it
labs/day01/checks/defaults.py    what the Check button verifies
```

Check imports your file (code under `if __name__ == "__main__":` is skipped), then calls your functions and reads your variables, so keep the names from the starter. Files you started before checks existed keep your code; if a check says a name is missing, save your work elsewhere and press **Reset to starter**. Non-Python files (Dockerfile, YAML, README) are checked as text. See `checker.py` for the helpers a check script can use.

## Things to know

- **Servers:** Day 2 and Week 2 have FastAPI apps. Run those in a separate terminal with `uvicorn` (the lesson shows the command); Bench stops any script after 60 seconds. Change the limit with the `RUN_TIMEOUT` environment variable.
- **Internet:** the code editor and fonts load from a CDN. Offline, Bench falls back to a plain text editor; everything else still works.
- **Your files are never overwritten:** starter code is only written to files that are missing or empty.
- **Progress** lives in `platform/progress.local.json`, which git ignores, so switching branches or pulling never touches it. On first start it carries over anything in the old `progress.json`. Back it up if you like.
- **Different lab location:** set `LAB_DIR` before starting, e.g. `set LAB_DIR=D:\code\my-work` (Windows) or `export LAB_DIR=...` (Mac/Linux).
- **Safety:** Bench listens only on 127.0.0.1 and runs the code you write on your own machine. Don't expose it to a network.

## The 12 weeks

All twelve weeks are in Bench, each with daily lessons, labs with checks, quizzes and a Sunday boss.

| Week | Dates | Topic | Needs on your machine |
|---|---|---|---|
| 1-2 | Oct 5-18 | Fundamentals, LLM basics and serving | Python |
| 3 | Oct 19-25 | RAG from scratch | Ollama (`bge-m3`), Docker for pgvector |
| 4 | Oct 26-Nov 1 | Evaluation | a model in Bench's AI settings |
| 5 | Nov 2-8 | Tool calling and agents, MCP | `mcp` package |
| 6 | Nov 9-15 | Real Arabic data (ARCD) | internet once, to download ARCD |
| 7 | Nov 16-22 | Scope your project: interview, targets, golden set | a real user |
| 8 | Nov 23-29 | Build I: parsing, OCR, indexing, citations, service | Tesseract with Arabic and French |
| 9 | Nov 30-Dec 6 | Build II: action tool, chat, streaming, web page, usability test | 3-5 test users |
| 10 | Dec 7-13 | Evaluate: grid, local vs API, intervals, cost, failures | |
| 11 | Dec 14-20 | Ship: tests, settings, logs, Docker Compose, CI, README | Docker, a GitHub repository |
| 12 | Dec 21-27 | Present: demo video, CV, LinkedIn, interviews, message to Anis | OBS (screen recording) |

From Week 7 on, the labs are the pieces of your own Phase 2 project: copy them into its repository as you go.

If a week's plan needs to change after a Sunday retro, tell Claude what you finished and what slipped; you'll get an updated week module (`curriculum_weekN.py`) and its `labs/dayNN/` folders. Replace them and refresh the page. Your progress and code are kept.
