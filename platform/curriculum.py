"""Full curriculum for Bench. Week 1 and Weeks 3+ live in curriculum_weekN.py; Week 2 is below.

To add next week's daily plan: append day dicts to that week's "days" list
(same shape as Week 1), or replace the file Claude sends you on Sunday.
"""
from curriculum_week1 import WEEK1
from curriculum_week3 import WEEK3
from lab_files import lab

PROJECT = "Document extraction service: messy real estate listings (Arabic, French, English) to clean JSON."

DAY8 = {
    "id": "w2d1", "folder": "day08", "notes_task": 4, "date": "2026-10-12", "weekday": "Mon",
    "title": "First LLM API calls", "minutes": 75,
    "why": "Everything in Phase 1 sits on this: prompts, tokens, and cost.",
    "lesson": r"""
:::hook
You run a small real estate agency in Sousse. Every morning 200 new listings arrive, in Arabic, French and English, and someone copies prices and surfaces into a spreadsheet by hand. An LLM can read each listing and fill the fields in a second. Before building that, you need to know three things: how to talk to a model, what one call costs, and how to keep the answers stable.
:::

## The shape of a call

A chat API is a function over HTTP. You send a **system prompt** (the model's job description) and a list of **messages**; you get back text plus a count of the tokens you used.

```python
request = {
    "system": "You extract real estate data. Reply with JSON only.",
    "messages": [{"role": "user", "content": "S+2 à Sahloul, 120 m², 250 000 DT"}],
    "temperature": 0,
    "max_tokens": 200,
}
response = {"text": '{"rooms": 3, "surface_m2": 120, "price_tnd": 250000}',
            "input_tokens": 41, "output_tokens": 19}
print(response["text"])
```

:::analogy
A call is like briefing a freelancer by email. The system prompt is their job description, the messages are the conversation so far, and they bill you per word you write **and** per word they write back. They remember nothing between emails: if you want them to know something, it goes in the email.
:::

:::check
? The model "forgets" what you told it in the previous call. Why?
- It has a short memory limit
* Each call is independent: only what you send in `messages` exists for the model
- The temperature was too high
> APIs are stateless. A chat "remembers" only because the app resends the whole history every time.
:::

## Temperature: stable or creative

Before writing each word the model has a list of possible next words with probabilities. **Temperature** decides how it picks. At 0 it almost always takes the most likely word, so the same prompt gives (nearly) the same answer. At 1.0 it samples more freely, so answers vary.

:::predict You ask "Give a name for a seaside apartment" 3 times at temperature 0, then 3 times at 1.0. What will you see?
---
At **0**: the same (or almost the same) name 3 times. At **1.0**: 3 different names. You'll verify it yourself in the exercise. For extraction you want 0: the price of a listing should not change between runs.
:::

:::key
Extraction, classification, anything with a right answer: temperature **0**. Brainstorming names or marketing text: around **0.7 to 1.0**.
:::

## Tokens are the unit of cost

Models don't read words, they read **tokens**: chunks of text of about 4 characters in English. Providers bill input and output tokens separately, per million. Output is usually 3 to 5 times more expensive than input.

```python
def call_cost(tokens_in, tokens_out, price_in_per_m, price_out_per_m):
    return (tokens_in * price_in_per_m + tokens_out * price_out_per_m) / 1_000_000

one = call_cost(500, 200, 3, 15)        # one listing
print(f"one call: ${one:.4f}")
print(f"1,000 listings: ${1000 * one:.2f}")
print(f"200 a day for a year: ${200 * 365 * one:.2f}")
```

:::predict Arabic text often costs more than the same sentence in English. Why do you think that is?
---
Tokenizers were trained mostly on English, so common English words are single tokens while Arabic words get cut into several smaller pieces. Same meaning, more tokens: more cost, and the context window fills faster. Keep this in mind for your Arabic project.
:::

:::reveal Why is output more expensive than input?
The model reads your whole input in one parallel pass, but it writes the output one token at a time, each token being a full pass through the network. Generating is the slow, costly part.
:::

## Free models for learning

You don't need to pay to learn this. In Bench, click **⚙ AI** in the header and pick one:

- **Google Gemini**: free key from Google AI Studio, generous for learning.
- **Groq**: free key, runs open models (Llama, Qwen) very fast.
- **Ollama**: open source models on your own computer. No key, no internet, totally free.

Paste the key, press **Save and test**. Your labs then use it with two lines:

```python
from bench_llm import get_client, current_model

client = get_client()   # same shape as anthropic.Anthropic()
msg = client.messages.create(model=current_model(), max_tokens=50, temperature=0,
                             system="Be brief.", messages=[{"role": "user", "content": "Say hi in Tunisian Arabic"}])
print(msg.content[0].text, msg.usage.input_tokens, msg.usage.output_tokens)
```

:::mistake
Never paste an API key into a `.py` file you commit to GitHub: bots scan public repos for keys within minutes. Bench keeps your key in `bench/llm_settings.local.json`, which git ignores. In your own projects, use environment variables.
:::

## Lock it in

:::cards
What are the 3 parts of a chat call? :: System prompt, messages, generation settings (temperature, max_tokens).
Temperature for extraction? :: 0, so answers are repeatable.
How is a call billed? :: Input tokens and output tokens, separately, per million.
Why does Arabic cost more? :: It splits into more tokens for the same meaning.
Does the model remember the last call? :: No. Calls are stateless; you resend the history.
:::

:::explain Explain to a friend who doesn't code why the same extraction job can cost more for Arabic listings than for English ones.
:::
""",
    "files": [
        lab("day08", "llm_basics.py", task=3),
    ],
    "tasks": [
        "Connect a free model in Bench (⚙ AI in the header): [Google AI Studio key](https://aistudio.google.com/apikey), [Groq key](https://console.groq.com/keys) or [Ollama](https://ollama.com/download)",
        "llm_basics.py: one call with a system prompt, tokens printed",
        "Compare temperature 0 vs 1.0",
        "Log tokens and cost per call",
        "Notes: what tokens are, and why Arabic often costs more",
    ],
    "done_when": "Every call logs tokens and cost.",
    "resources": [],
    "quiz": [
        {"q": "1,000 calls of 500 input + 200 output tokens at $3/M input and $15/M output. Total?", "options": ["$0.45", "$4.50", "$18.00", "$45.00"], "answer": 1,
         "explain": "Per call: 500 x 3 + 200 x 15 = 4,500 per million = $0.0045. Times 1,000 = $4.50."},
        {"q": "For extracting fields from documents, temperature should usually be...", "options": ["0 or close to it", "1.0", "2.0", "It doesn't matter"], "answer": 0,
         "explain": "Low temperature gives consistent, repeatable output."},
    ],
}

DAY9 = {
    "id": "w2d2", "folder": "day09", "notes_task": 3, "date": "2026-10-13", "weekday": "Tue",
    "title": "Structured output", "minutes": 75,
    "why": "Real systems need JSON they can trust, not free text.",
    "lesson": r"""
:::hook
Your extractor works 9 times out of 10. On the 10th listing the model answers `"rooms": "three"` or wraps the JSON in a sentence ("Sure! Here is the JSON: ..."). Your pipeline crashes at 3 a.m. Today you make the output something your code can **trust**.
:::

## Schema first

Decide the exact shape of the answer before you write the prompt. Pydantic turns that shape into a Python class that checks every value.

```python
from pydantic import BaseModel, ValidationError

class Listing(BaseModel):
    price_tnd: float | None
    surface_m2: float | None
    rooms: int | None
    city: str | None

good = '{"price_tnd": 250000, "surface_m2": 120, "rooms": 3, "city": "Sousse"}'
print(Listing.model_validate_json(good))
```

:::analogy
The schema is a customs officer. Every answer that comes back from the model has to show its papers: right fields, right types. Anything suspicious is stopped at the border instead of wandering into your database.
:::

:::predict What happens if `rooms` comes back as `"three"`? And as `"3"`?
```python
from pydantic import BaseModel, ValidationError

class Listing(BaseModel):
    rooms: int | None

for raw in ['{"rooms": "three"}', '{"rooms": "3"}']:
    try:
        print(raw, "->", Listing.model_validate_json(raw))
    except ValidationError as e:
        print(raw, "-> ValidationError:", e.errors()[0]["msg"])
```
---
`"three"` fails with a ValidationError. `"3"` passes and becomes the int `3`: Pydantic converts numbers written as strings (lax mode). Press **Run ▶** above to see it.
:::

## Put the schema in the prompt

The model can't follow rules it hasn't seen. Paste the JSON schema into the prompt and ask for JSON only.

```python
import json
from pydantic import BaseModel

class Listing(BaseModel):
    price_tnd: float | None
    rooms: int | None

prompt = (
    "Extract the fields from this listing. Reply with JSON ONLY matching this schema:\n"
    + json.dumps(Listing.model_json_schema())
    + "\n\nListing: S+2 à Sahloul, 250 000 DT"
)
print(prompt)
```

## Validate, then retry once

When validation fails, don't give up and don't loop forever. Send the error message back and ask for a corrected JSON. The model is good at fixing a mistake it can see.

:::check
? The first answer fails validation. What is the best next move?
- Retry the exact same prompt 5 times
* Retry once, adding the validation error to the prompt
- Fix the JSON yourself with string replacements
- Lower max_tokens
> The error tells the model exactly what was wrong. One informed retry fixes most failures; log the rest for review.
:::

## Never eval model output

:::mistake
`eval(reply)` would run whatever text the model produced as Python code. A listing containing a prompt injection could make it run `__import__('os').remove(...)`. Parse with `json.loads` or Pydantic, always.
:::

:::cards
Why define a schema first? :: So every answer is checked: right fields, right types.
What does model_validate_json do? :: Parses JSON and validates it against the class, raising ValidationError if wrong.
What goes in a retry prompt? :: The original task plus the validation error.
How many retries? :: One. Then log the failure.
eval() on model output? :: Never: it executes untrusted text.
:::

:::explain Why is "validate + one retry with the error" better than just retrying the same prompt?
:::
""",
    "files": [
        lab("day09", "listings.json"),
        lab("day09", "structured.py", task=[1, 2]),
    ],
    "tasks": [
        "Collect 10 real listings (e.g. [Tayara](https://www.tayara.tn), [Mubawab](https://www.mubawab.tn)) and hand-label price, surface, rooms, city",
        "Define the Pydantic schema ([Pydantic models](https://docs.pydantic.dev/latest/concepts/models/))",
        "Prompt for JSON, validate, retry once on failure",
        "Notes: which fields fail most and why",
    ],
    "done_when": "10 listings in, 10 validated JSON objects out.",
    "resources": [{"label": "Pydantic docs", "url": "https://docs.pydantic.dev"}],
    "quiz": [
        {"q": "The model returns JSON with rooms as \"three\". Best handling?", "options": ["eval() it", "Accept it as is", "Validate with Pydantic and retry with the error message", "Drop the listing silently"], "answer": 2,
         "explain": "Validation catches it; feeding the error back usually gets a corrected answer."},
        {"q": "Why never eval() model output?", "options": ["It's slow", "It can execute arbitrary code", "It loses Unicode", "It only works on dicts"], "answer": 1,
         "explain": "Generated text is untrusted input."},
    ],
}

DAY10 = {
    "id": "w2d3", "folder": "day10", "date": "2026-10-14", "weekday": "Wed",
    "title": "Run an open model yourself", "minutes": 75,
    "why": "Self-hosting is the cost and privacy alternative you'll compare against the API.",
    "lesson": r"""
:::hook
Your client is a notary office. Their listings contain owners' names and phone numbers, and their lawyer says: **no data leaves the building**. A cloud API is out. The answer is to run an open model on your own machine.
:::

## Ollama in two commands

Ollama downloads open models (Qwen, Llama, Mistral...) and runs them locally.

```bash
ollama pull qwen2.5:3b
ollama run qwen2.5:3b "Say hello in Arabic"
```

:::analogy
An API is a restaurant: great food, you pay per dish, and your order goes to their kitchen. Ollama is cooking at home: you buy the equipment once (your RAM/GPU), nothing leaves your house, and each meal is free, but you're limited by your kitchen.
:::

:::check
? Your laptop has 8 GB of RAM and no GPU. Which model size is realistic?
* A 3B model (about 2 GB quantized)
- A 70B model
- Any size, Ollama compresses everything
> 3B runs on most laptops. 7B wants more RAM or a GPU. 70B needs a serious server.
:::

## Call it from Python

Ollama serves an HTTP API on `http://localhost:11434`. It's just a POST request, like any other API.

```python
import httpx

resp = httpx.post("http://localhost:11434/api/chat", json={
    "model": "qwen2.5:3b",
    "messages": [{"role": "user", "content": "Return {\"ok\": true} as JSON."}],
    "format": "json",
    "stream": False,
}, timeout=120)
print(resp.json()["message"]["content"])
```

:::key
Ollama also speaks the OpenAI format at `http://localhost:11434/v1`, which is why Bench can use it for the tutor: pick **Ollama** in ⚙ AI.
:::

## Quantization

A model's weights are numbers. Stored at 16 bits each, a 3B model takes about 6 GB. **Quantized** to 4 bits, about 2 GB, at a small cost in quality.

:::predict Roughly how much memory does a 7B model need at 4 bits? (Hint: 4 bits = half a byte.)
---
7 billion x 0.5 byte ≈ **3.5 GB**, plus some overhead: about 4-5 GB in practice. At 16 bits it would be about 14 GB.
:::

## Cold start

The first call loads the model from disk into memory, so it can take 10x longer than the next ones.

:::mistake
Timing the very first call and reporting it as "latency". Always send one warm-up call, then measure.
:::

:::cards
Why run a model locally? :: Privacy (data stays on the machine) and no per-call cost.
What does 4-bit quantization trade? :: Much less memory for a small quality loss.
Ollama's default port? :: 11434
Why is the first call slow? :: Cold start: the model loads into memory.
:::

:::explain When would you recommend a local model to a client, and when an API? Give one reason for each.
:::
""",
    "files": [
        lab("day10", "local_model.py"),
    ],
    "tasks": [
        "[Install Ollama](https://ollama.com/download) and pull a small [Qwen2.5 model](https://ollama.com/library/qwen2.5)",
        "Run the 10 extractions locally with latency per call",
        "Compare field accuracy with the API model",
        "PFE: finish the host list ([LinkedIn Jobs](https://www.linkedin.com/jobs/search/?keywords=PFE%20machine%20learning&location=Tunisia))",
    ],
    "done_when": "Accuracy and latency for both models on the same 10 inputs.",
    "resources": [{"label": "Ollama", "url": "https://ollama.com"}],
    "quiz": [
        {"q": "Why is the first local call much slower?", "options": ["Network latency", "The model loads into memory (cold start)", "Ollama compiles the prompt", "Quantization runs first"], "answer": 1,
         "explain": "Always warm up before measuring."},
        {"q": "What does 4-bit quantization trade?", "options": ["Speed for accuracy", "Memory savings for a small quality loss", "Context length for speed", "Nothing"], "answer": 1,
         "explain": "Smaller weights, slightly less precise outputs."},
    ],
}

DAY11 = {
    "id": "w2d4", "folder": "day11", "date": "2026-10-15", "weekday": "Thu",
    "title": "Wrap it in FastAPI", "minutes": 75,
    "why": "A model isn't a product until it's a service. Apply Day 2's async lesson for real.",
    "lesson": r"""
:::hook
Your extractor works in a script. Now the agency's website wants to call it: a user pastes a listing and gets clean fields back. A script can't do that; a **web service** can. And when 20 agents use it at once, it must not make them queue.
:::

## The endpoint

`POST /extract` takes listing text (and a model choice) and returns validated JSON. FastAPI checks the incoming body with the same Pydantic models you know.

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ExtractIn(BaseModel):
    text: str

@app.post("/extract")
async def extract(body: ExtractIn):
    return {"chars": len(body.text)}   # the model call goes here
print([r.path for r in app.routes][-1])
```

## Async done right

:::analogy
A waiter (the event loop) serves many tables. `await` means "I've sent the order to the kitchen, I'll serve other tables meanwhile". Calling `requests` inside `async def` is a waiter standing frozen at the kitchen door until the dish is ready: every other table waits.
:::

:::check
? Inside `async def extract`, you call Ollama with `requests.post(...)`. What happens when 5 users call at once?
- They run in parallel, fine
* They are served one after another: each blocks the event loop
- FastAPI raises an error
> `requests` is blocking. Use `httpx.AsyncClient` with `await` so the loop keeps serving others. You measured exactly this on Day 2.
:::

## Honest status codes

The status code tells the caller **whose fault** a failure is.

- **422**: the client's request is invalid (FastAPI does this automatically for bad bodies).
- **502 Bad Gateway**: your upstream (the model) returned something unusable.
- **504 Gateway Timeout**: the model took too long.

:::predict The model answers, but even after one retry the JSON is invalid. Which code, and why not 500?
---
**502**. The client did nothing wrong (not 4xx), and your server didn't crash either: the upstream model gave a bad answer. 500 means "my own code broke", which hides the real cause.
:::

Run the service in your terminal (Bench stops scripts after 60 s):

```bash
cd ml-fundamentals-lab/day11
uvicorn service:app --port 8002 --reload
```

:::cards
Which client inside async def? :: httpx.AsyncClient with await.
Bad request body? :: 422, FastAPI does it for you.
Model gave unusable output? :: 502 Bad Gateway.
Model too slow? :: 504 Gateway Timeout.
:::

:::explain Explain to a frontend developer what 422, 502 and 504 from your API mean and what they should show the user for each.
:::
""",
    "files": [
        lab("day11", "service.py", task=[0, 1]),
        lab("day11", "concurrency_check.py"),
    ],
    "tasks": [
        "POST /extract with async model calls",
        "Validation, one retry, 502 and 504 errors",
        "Prove concurrency with your Day 2 load test",
    ],
    "done_when": "Concurrent requests don't block each other.",
    "resources": [{"label": "HTTPX async client", "url": "https://www.python-httpx.org/async/"}],
    "quiz": [
        {"q": "Inside async def, which client should call Ollama?", "options": ["requests", "httpx.AsyncClient with await", "urllib", "subprocess curl"], "answer": 1,
         "explain": "It's awaitable, so the loop keeps serving other requests."},
        {"q": "The model returns unparseable output after a retry. Status code?", "options": ["200", "400", "422", "502"], "answer": 3,
         "explain": "The client's request was fine; the upstream failed."},
    ],
}

DAY12 = {
    "id": "w2d5", "folder": "day12", "date": "2026-10-16", "weekday": "Fri",
    "title": "Measure", "minutes": 75,
    "why": "Anis asked for accuracy, cost, and latency. Today you produce that table.",
    "lesson": r"""
:::hook
Your manager asks: "Should we use the API or the local model?" "The local one feels fine" is not an answer. A table with **accuracy, latency and cost** is. Today you produce it.
:::

## Accuracy, per field

Compare each predicted field to your hand-written label, then average. Per field tells you *where* the model fails (often `surface_m2`).

```python
label = {"price_tnd": 250000, "surface_m2": 120, "rooms": 3, "city": "Sousse"}
pred  = {"price_tnd": 250000, "surface_m2": None, "rooms": 3, "city": "sousse"}
hits = [pred[k] == label[k] for k in label]
print(hits, sum(hits) / len(hits))
```

:::mistake
`"sousse" != "Sousse"`: a fair comparison normalizes strings first (lowercase, strip spaces). Decide your rule and apply it to both models.
:::

## Latency: p50 and p95

:::predict 10 calls take these seconds: 0.8, 0.9, 1.1, 0.7, 4.2, 0.9, 1.0, 0.8, 0.9, 5.1. Is the mean a good summary of what users feel?
```python
import statistics
latencies = [0.8, 0.9, 1.1, 0.7, 4.2, 0.9, 1.0, 0.8, 0.9, 5.1]
q = statistics.quantiles(latencies, n=100, method="inclusive")
print("mean", round(statistics.mean(latencies), 2), "p50", round(q[49], 2), "p95", round(q[94], 2))
```
---
No. The mean (about 1.6 s) describes nobody: most calls take about 0.9 s (**p50**), and 1 in 10 users waits 4-5 s (**p95**). Report both: p50 is the typical experience, p95 is the complaint.
:::

:::analogy
p50 is how long the bus usually takes. p95 is the day it's late and you miss your meeting. Riders remember p95.
:::

## Cost per 1,000 requests

Average your token counts, then multiply with yesterday's `call_cost`. For the local model, write the hardware instead ("laptop, 16 GB RAM, CPU only"): its cost is the machine.

:::check
? Why run each input 3 times?
- To get 3x more accuracy
* To see variance: latency and even answers change between runs
- Providers require it
> One run can be lucky or unlucky. Three runs show how stable your numbers are.
:::

:::cards
p50 :: The median: half the calls are faster.
p95 :: 95% are faster: the slow tail users notice.
Why not only the mean? :: A few very slow calls hide inside it.
Local model cost? :: Write the hardware it ran on.
:::

:::explain Your table says API: 0.95 accuracy, p95 2.1 s, $0.40 / 1k. Local: 0.82, p95 6.5 s, free. Write the 3-line recommendation you'd send your manager.
:::
""",
    "files": [
        lab("day12", "measure.py"),
    ],
    "tasks": [
        "measure.py: both models, 10 listings, 3 runs",
        "Field accuracy, p50/p95 latency, cost per 1,000 requests",
        "Results table saved as results.md",
    ],
    "done_when": "One table comparing both models on accuracy, latency, and cost.",
    "resources": [],
    "quiz": [
        {"q": "Why report p95 latency, not just the mean?", "options": ["It's always lower", "It shows the slow tail users actually feel", "It's easier to compute", "Providers require it"], "answer": 1,
         "explain": "A few very slow calls hide inside a mean."},
    ],
}

DAY13 = {
    "id": "w2d6", "folder": "day13", "date": "2026-10-17", "weekday": "Sat",
    "title": "Ship it", "minutes": 180,
    "why": "A repo someone can run with one command is portfolio proof.",
    "lesson": r"""
:::hook
A recruiter opens your GitHub. If running your project takes 12 manual steps, they close the tab. If it's `docker compose up`, they try it. Today your service becomes **one command**.
:::

## Docker in one picture

:::analogy
A Docker **image** is a frozen lunchbox: your code, Python, and every library, packed exactly as on your machine. A **container** is that lunchbox opened and running. "Works on my machine" becomes "works in this box, on any machine".
:::

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY service.py .
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "8002"]
```

:::predict Why copy `requirements.txt` and install **before** copying `service.py`?
---
Docker caches each step. If only `service.py` changes, the slow `pip install` layer is reused and the rebuild takes seconds. Copy everything first and every code edit reinstalls all packages.
:::

## Two containers

The service and Ollama run as two services in Docker Compose. Inside the Compose network, containers reach each other by **service name**, not `localhost`.

```yaml
services:
  api:
    build: .
    ports: ["8002:8002"]
    environment:
      OLLAMA_URL: http://ollama:11434
    depends_on: [ollama]
  ollama:
    image: ollama/ollama
    volumes: [ollama:/root/.ollama]
volumes:
  ollama:
```

:::check
? Inside the `api` container, what does `localhost` point to?
* The api container itself
- Your laptop
- The ollama container
> Each container has its own localhost. Use the service name `ollama` to reach the other one.
:::

:::reveal Why a named volume for Ollama?
Models are gigabytes. Without the volume, every `docker compose down` deletes the downloaded model and the next start pulls it again.
:::

## The README that gets read

Problem, architecture sketch, results table, one-command run instructions, and what you'd improve. A recruiter reads the first screen only: put the result table high.

:::cards
Image vs container? :: Image = the packed lunchbox. Container = it running.
Why COPY requirements first? :: Layer caching: code changes don't reinstall packages.
API reaches Ollama at? :: http://ollama:11434 (service name).
Why host 0.0.0.0 in CMD? :: So the server accepts connections from outside the container.
:::

:::explain Explain why `http://localhost:11434` works on your laptop but fails inside the api container.
:::
""",
    "files": [
        lab("day13", "Dockerfile", task=0),
        lab("day13", "docker-compose.yml", task=0),
        lab("day13", "README.md", task=1),
    ],
    "tasks": [
        "Dockerfile and docker-compose.yml (API + Ollama), see the [Compose docs](https://docs.docker.com/compose/)",
        "README with the results table",
        "Push as a public repo ([create llm-extraction-service](https://github.com/new)) and [pin it](https://github.com/OussemaBouchaala)",
        "PFE: send your first 2 applications ([LinkedIn Jobs](https://www.linkedin.com/jobs/search/?keywords=PFE%20machine%20learning&location=Tunisia))",
    ],
    "done_when": "Someone can clone the repo and run it with one command.",
    "resources": [{"label": "Docker Compose docs", "url": "https://docs.docker.com/compose/"}],
    "quiz": [
        {"q": "Inside Compose, how does the api container reach Ollama?", "options": ["http://localhost:11434", "http://ollama:11434", "http://127.0.0.1:11434", "It can't"], "answer": 1,
         "explain": "Each container has its own localhost; service names resolve on the Compose network."},
    ],
}

DAY14 = {
    "id": "w2d7", "folder": "day14", "date": "2026-10-18", "weekday": "Sun",
    "title": "Retro and RAG prep", "minutes": 150,
    "why": "Week 3 is RAG. Embeddings and vector search are its foundation.",
    "lesson": r"""
:::hook
Next week a user will ask "What does the law say about rent increases?" and your system must find the right paragraph among thousands, even if it says "augmentation du loyer" or "زيادة الكراء". Keyword search fails here. Search **by meaning** doesn't.
:::

## Embeddings

An embedding model turns text into a list of numbers (a vector) so that **similar meanings land close together**, whatever the words or the language.

:::analogy
Imagine a giant map where every sentence is a city. "Rent increase", "augmentation du loyer" and "زيادة الكراء" are neighbouring towns. "Football match" is on another continent. Search = find the towns closest to the question's town.
:::

## Cosine similarity

Closeness is measured by the **angle** between vectors: same direction = 1, unrelated = 0, opposite = -1.

```python
import numpy as np

def cosine(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

q = np.array([0.9, 0.1, 0.0])
docs = {"rent law": np.array([0.8, 0.2, 0.1]), "football": np.array([0.0, 0.1, 0.9])}
for name, v in docs.items():
    print(name, round(cosine(q, v), 3))
```

:::predict What is `cosine([1, 2], [10, 20])`?
---
**1.0**. The second vector is 10x longer but points in exactly the same direction. Cosine ignores length, which is why a long document and a short question can still match.
:::

:::check
? Why cosine and not plain distance between the points?
* Cosine compares direction (meaning), not length (often just text size)
- Distance is too slow to compute
- Cosine is always positive
> Length often reflects how much text there is, not what it means.
:::

## pgvector

A PostgreSQL extension that stores vectors in a column and searches them by distance, so your documents, metadata and vectors live in one database you already know.

:::cards
What is an embedding? :: A vector representing meaning; similar meanings are close.
Cosine of same-direction vectors? :: 1, whatever their lengths.
Why does it work across languages? :: Multilingual models map the same meaning to nearby vectors.
pgvector? :: Postgres extension to store and search vectors.
:::

:::explain Explain to a non-technical client why "search by meaning" finds an Arabic paragraph for a French question.
:::
""",
    "files": [
        lab("day14", "embeddings_intro.py", task=1),
    ],
    "tasks": [
        "Read about [embeddings](https://huggingface.co/blog/getting-started-with-embeddings) and cosine similarity; read the [pgvector README](https://github.com/pgvector/pgvector#readme)",
        "embeddings_intro.py: cosine similarity and ranking",
        "Choose and download the Arabic corpus for Weeks 3-6 ([Arabic datasets on Hugging Face](https://huggingface.co/datasets?language=language:ar))",
        "Weekly retro: tick the tracker and [send Claude](https://claude.ai) your progress",
    ],
    "done_when": "The corpus is on disk and you know how pgvector stores and searches vectors.",
    "resources": [{"label": "pgvector", "url": "https://github.com/pgvector/pgvector"}],
    "quiz": [
        {"q": "Cosine similarity of two vectors pointing the same direction (any lengths)?", "options": ["0", "1", "-1", "Depends on length"], "answer": 1,
         "explain": "Cosine measures angle, not magnitude."},
    ],
}

WEEK2 = {
    "n": 2, "phase": "Phase 1", "title": "LLM basics and serving", "dates": "Oct 12-18",
    "goal": PROJECT,
    "gate": "Repo with a results table for API vs local model",
    "days": [DAY8, DAY9, DAY10, DAY11, DAY12, DAY13, DAY14],
}


def roadmap_week(n, phase, title, dates, goal, tasks, gate):
    return {"n": n, "phase": phase, "title": title, "dates": dates, "goal": goal,
            "gate": gate, "days": [], "tasks": tasks}


CURRICULUM = [
    WEEK1,
    WEEK2,
    WEEK3,
    roadmap_week(4, "Phase 1", "Evaluation", "Oct 26-Nov 1",
                 "An eval script and a results table.",
                 ["Test set of 50-100 questions with expected answers", "Retrieval recall@k",
                  "Answer faithfulness (LLM-as-judge or [RAGAS](https://docs.ragas.io))", "Latency and cost per query"], "Eval table"),
    roadmap_week(5, "Phase 1", "Tool calling and agents", "Nov 2-8",
                 "An agent that performs one real action.",
                 ["Function calling with tool schemas ([Anthropic tool use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use), [OpenAI function calling](https://platform.openai.com/docs/guides/function-calling))", "Agent calling your own FastAPI endpoints", "[MCP](https://modelcontextprotocol.io) basics"],
                 "Working agent"),
    roadmap_week(6, "Phase 1", "Real Arabic data", "Nov 9-15",
                 "Arabic RAG prototype with eval numbers.",
                 ["Pick and load a public Arabic corpus ([Hugging Face](https://huggingface.co/datasets?language=language:ar))", "Normalization: alef/hamza, taa marbuta, diacritics",
                  "Mixed Arabic/English/French text", "Re-run the Week 4 eval on Arabic questions"],
                 "Arabic RAG prototype with eval numbers"),
    roadmap_week(7, "Phase 2", "Scope the project", "Nov 16-22",
                 "One-page problem statement with a real user and data.",
                 ["Choose the project option", "Confirm the real user and data access",
                  "Success metrics: accuracy, latency, cost targets"], "Signed-off scope"),
    roadmap_week(8, "Phase 2", "Build I", "Nov 23-29",
                 "Ingestion and retrieval working end to end.",
                 ["Ingestion pipeline (OCR/parsing, chunking, indexing)", "Retrieval + generation with citations"],
                 "End-to-end path works"),
    roadmap_week(9, "Phase 2", "Build II", "Nov 30-Dec 6",
                 "Tool calling and a usable UI.",
                 ["Tool calling for at least one real action", "Simple web UI"], "Usable demo"),
    roadmap_week(10, "Phase 2", "Evaluate", "Dec 7-13",
                 "Two configurations compared on accuracy, latency, cost.",
                 ["Compare self-hosted vs API, with vs without reranker", "Results table", "Failure cases written up"],
                 "Results table"),
    roadmap_week(11, "Phase 2", "Ship", "Dec 14-20",
                 "Deployable, documented, tested.",
                 ["[Docker Compose](https://docs.docker.com/compose/) deployment", "README and architecture diagram", "Tests for core functions"],
                 "One-command run"),
    roadmap_week(12, "Phase 2", "Present", "Dec 21-27",
                 "Demo video and the message to Anis.",
                 ["3-5 minute demo video", "Update CV and [LinkedIn](https://www.linkedin.com/)", "Send the follow-up message to Anis"],
                 "Message sent"),
]
