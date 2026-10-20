"""Week 10: Evaluate (Dec 7-13, 2026)."""
from lab_files import lab

DAY64 = {
    "id": "w10d1", "folder": "day64", "date": "2026-12-07", "weekday": "Mon",
    "title": "The experiment grid", "minutes": 75,
    "why": "Anis asked for a comparison. Running configs by hand, one by one, you'll lose track of which number came from what.",
    "lesson": r"""
:::hook
Thursday night, 11 runs in, the laptop sleeps. Which configs are done? Did run 7 use the new golden set or the old one? You re-run everything to be safe: four hours. A run log with stable keys would have resumed in a second.
:::

## Expand, then prune

2 models × 2 rerank × 3 k × 2 search = 24 runs. Some combinations make no sense (reranking 3 chunks). Drop them with rules before running.

```python
import itertools
space = {"model": ["local", "api"], "rerank": [False, True], "k": [3, 5, 10]}
grid = [dict(zip(space, v)) for v in itertools.product(*space.values())]
grid = [c for c in grid if not (c["rerank"] and c["k"] < 5)]
print(len(grid), "runs")
```

:::analogy
A chef testing a new sauce: 3 spice levels × 2 cooking times × 2 creams = 12 pots. Before cooking, they cross out "very spicy + extra cream" because it's known to curdle.
:::

## Name and key every run

- **Name**: readable, sorted keys: `k=5|model=api|rerank=True`.
- **Key**: hash of config **and data version**. Change the golden set → new keys → those runs happen again. Same set → skipped.

## Append, flush, resume

One JSON line per finished run, flushed immediately. On restart, read the keys, skip what's done. A crash mid-write leaves a broken last line: ignore it.

:::predict You add 5 questions to the golden dev set. Which runs re-run?
---
All of them: the data version changed, so every key is new. That's correct, because old numbers were computed on different questions and can't be compared with new ones.
:::

:::check
? Why include the dataset version in the run key?
- To make keys longer
* So results computed on different questions are never mixed in one table
- For sorting
- JSON requires it
> Comparable numbers come from the same data.
:::

:::mistake
Running the grid on the **test** set. The grid is tuning; it uses dev. Test is for the 2-3 finalists, once, on Saturday.
:::

:::cards
Prune the grid with? :: Rules that drop pointless combinations.
Run key includes? :: The config and the data version.
Resume after a crash? :: Read done keys from the JSONL log; skip them.
Broken last line? :: Ignore it; that run re-runs.
Grid runs on? :: Dev. Finalists on test, once.
:::

:::explain Explain why you hash the dataset into the run key.
:::
""",
    "files": [
        lab("day64", "experiment_grid.py", task=[0, 1]),
    ],
    "tasks": [
        "experiment_grid.py: expand, filter, name, key",
        "Run log with resume; start the grid on the dev set",
        "Cut the grid to what you can run this week (aim for 8-12 configs)",
    ],
    "done_when": "The grid runs, stops, and resumes without redoing finished configs.",
    "resources": [],
    "quiz": [
        {"q": "The grid should run on...", "options": ["The test set", "The dev set", "Both, every time", "Production traffic"], "answer": 1,
         "explain": "Tuning on test makes the final number optimistic."},
        {"q": "Why flush after each result?", "options": ["Speed", "A crash loses at most the current run", "JSON needs it", "Sorting"], "answer": 1,
         "explain": "Buffered lines vanish when the process dies."},
    ],
}

DAY65 = {
    "id": "w10d2", "folder": "day65", "notes_task": 2, "date": "2026-12-08", "weekday": "Tue",
    "title": "Local vs API model", "minutes": 75,
    "why": "The privacy-vs-quality question is the one the agency will ask. Answer it on their questions, per category.",
    "lesson": r"""
:::hook
Local model: 0.79 correct. API model: 0.86. "The API is better by 7 points." But per category: the local model wins on French fees questions and loses badly on Derja. That's not "7 points worse"; that's "fine in French, not ready for Derja".
:::

## Per category, not just overall

An overall mean averages away the story. Break scores down by category and language, where your interview said the pain was.

## Pairwise judging, both orders

Instead of scoring each answer alone, show the judge both answers and ask which is better. Judges prefer whichever answer they read **first** (position bias). So judge (A, B) and (B, A); a model wins only if it wins both times.

```python
def outcome(ab, ba):
    return "model1" if (ab, ba) == ("A", "B") else "model2" if (ab, ba) == ("B", "A") else "tie"
pairs = [("A", "B"), ("A", "A"), ("B", "A"), ("B", "B")]
print([outcome(*p) for p in pairs])
```

:::analogy
A blind taste test where each glass is tasted in both orders. If the taster always prefers the first glass, that's not a preference for a wine.
:::

## Paired counts

On the same questions: how many does only model 1 get right? Only model 2? If "only 2" is 9 and "only 1" is 2, the difference is real even if both overall scores look close.

:::predict A judge says "A" in both orders for 30% of pairs. What does that tell you?
---
Strong position bias: those 30% are ties, not wins. Report how often it happens; if it's high, try a different judge prompt or model.
:::

:::check
? Why parse the verdict from the LAST verdict word or a [[X]] tag?
- It's easier
* Judges discuss both answers before deciding; early mentions of "A" aren't the verdict
- The first word is always wrong
- To save tokens
> Ask for a fixed format, and parse defensively.
:::

:::mistake
Comparing a local model with a short prompt against an API model with a carefully tuned one. Same prompt, same retrieval, same chunks: change only the model.
:::

:::cards
Position bias? :: Judges favor the first answer shown.
Fix? :: Judge both orders; count consistent wins only.
Win rate? :: (wins + 0.5 × ties) / n.
Paired counts? :: only1 / only2 / both / neither on shared questions.
Fair comparison? :: Same prompt and retrieval, only the model changes.
:::

:::explain Explain to the agency manager where the local model is good enough and where it isn't.
:::
""",
    "files": [
        lab("day65", "compare_models.py", task=[0, 1]),
    ],
    "tasks": [
        "compare_models.py: per_category, paired",
        "parse_preference, debias, win_rate; judge your two models on dev",
        "Write one sentence per category: which model, and why",
    ],
    "done_when": "A per-category table and a debiased win rate for local vs API.",
    "resources": [{"label": "Judging LLM-as-a-judge (position bias)", "url": "https://arxiv.org/abs/2306.05685"}],
    "quiz": [
        {"q": "The judge says A in both orders. Outcome?", "options": ["Model 1 wins", "Model 2 wins", "Tie (position bias)", "Discard the question"], "answer": 2,
         "explain": "No consistent preference."},
        {"q": "Why per-category scores?", "options": ["Prettier tables", "An average hides where each model fails", "Required by judges", "Smaller numbers"], "answer": 1,
         "explain": "Derja failures vanish into a French-heavy average."},
    ],
}

DAY66 = {
    "id": "w10d3", "folder": "day66", "date": "2026-12-09", "weekday": "Wed",
    "title": "Confidence intervals", "minutes": 75,
    "why": "On 40 questions, a 4-point difference can be pure luck. Intervals stop you from shipping noise.",
    "lesson": r"""
:::hook
Config B scores 0.82, config A 0.78, on 50 questions. You switch to B, it's slower and costs more. Next month, on new questions, B scores 0.77. It was never better: 2 questions out of 50 flipped by chance.
:::

## The bootstrap

You can't collect 10 more golden sets. But you can **resample** the one you have: draw 50 questions with replacement, compute the score, repeat 2,000 times. The spread of those scores approximates how much the score would move with different questions.

```python
import random
scores = [1] * 39 + [0] * 11
rng = random.Random(0)
means = sorted(sum(rng.choices(scores, k=50)) / 50 for _ in range(2000))
print(f"0.78 [{means[50]:.2f}, {means[1949]:.2f}]")
```

:::analogy
Estimating a city's average rent from 50 listings. Re-drawing different subsets of your 50 listings shows how much the estimate wobbles; if it wobbles by 200 TND, don't claim precision to the dinar.
:::

## Paired: resample questions, keep the pairs

To compare A and B, resample **question indexes** and compute A − B on the same resampled questions. Because both configs face the same hard questions, the paired interval is much narrower than comparing two separate intervals.

:::predict A: 0.78 [0.66, 0.88]. B: 0.82 [0.70, 0.92]. The intervals overlap. Is B definitely not better?
---
Not necessarily. Overlapping separate intervals don't settle it; the **paired** difference interval does. If A − B is [−0.10, −0.01], B is better; if it's [−0.10, 0.03], you can't tell.
:::

## How many questions would you need?

For ±5 points around 80%, about 246 questions. For ±10, about 62. That's why your report says "the intervals are wide", and why the golden set should grow with feedback.

:::check
? The paired difference interval is [−0.02, 0.09]. What do you report?
- B is better
- A is better
* No significant difference on this test set
- The test failed
> 0 is inside: the data can't separate them.
:::

:::mistake
Resampling answers independently for A and B. That breaks the pairing and throws away the fact that both faced the same questions; your interval comes out too wide.
:::

:::cards
Bootstrap? :: Resample the data with replacement, recompute, look at the spread.
95% percentile interval? :: The 2.5th and 97.5th percentiles of the resampled means.
Paired bootstrap? :: Resample question indexes; compute A − B on them.
Significant? :: 0 outside the difference interval.
±5 points at 80%? :: About 246 questions.
:::

:::explain Explain "0.78 [0.66, 0.88]" to the agency manager in one sentence.
:::
""",
    "files": [
        lab("day66", "bootstrap.py", task=[0, 1]),
    ],
    "tasks": [
        "bootstrap.py: bootstrap_ci, format_ci",
        "paired_bootstrap_diff, significant, questions_needed",
        "Add intervals to your grid's top 3 configs; note which differences are real",
    ],
    "done_when": "Your top configs have intervals, and you know which differences are significant.",
    "resources": [{"label": "Bootstrapping (Wikipedia)", "url": "https://en.wikipedia.org/wiki/Bootstrapping_(statistics)"}],
    "quiz": [
        {"q": "The difference interval is [0.01, 0.12]. Conclusion?", "options": ["No difference", "A is significantly better", "Need a judge", "B is better"], "answer": 1,
         "explain": "0 is outside, positive side: A − B > 0."},
        {"q": "Why resample question indexes for paired comparison?", "options": ["Faster", "Both configs stay on the same questions", "Fewer samples", "No reason"], "answer": 1,
         "explain": "Pairing cancels out question difficulty."},
    ],
}

DAY67 = {
    "id": "w10d4", "folder": "day67", "notes_task": 2, "date": "2026-12-10", "weekday": "Thu",
    "title": "The cost model", "minutes": 75,
    "why": "The agency will ask \"how much per month?\". Answer in TND, for their volume, with the point where the answer changes.",
    "lesson": r"""
:::hook
"Local is free." Except the GPU PC costs 900 USD, draws 180 W ten hours a day, and someone has to keep Ollama running. "The API is cheap." Except a large model at 2,500 input tokens per question costs 4x the small one. At 2,000 questions a month, one is 25 TND and another 94 TND.
:::

## Per-query API cost

`(input tokens × input price + output tokens × output price) / 1,000,000`, with **prompt caching**: the instructions and system prompt repeat every time, and cached input is billed at about 10% of the price.

```python
price = {"in": 0.80, "out": 4.00, "cached_in": 0.08}
inp, out, hit = 2500, 250, 0.4
cost = (inp * (1 - hit) * price["in"] + inp * hit * price["cached_in"] + out * price["out"]) / 1e6
print(f"{cost:.5f} USD per question, {cost * 2000:.2f} USD per month at 2,000 questions")
```

## Local cost per month

Electricity (watts × hours × days × price per kWh) plus the hardware spread over its life (36 months). Plus your time, which you should at least mention.

:::analogy
Taxi vs buying a car. Taxis win if you ride twice a week; the car wins if you drive daily. The break-even is the number of rides a month where both cost the same.
:::

## Break-even and capacity

- **Break-even**: local monthly cost ÷ API cost per query = the volume above which local is cheaper.
- **Capacity**: at peak (Saturday morning, 6 questions a minute, 8 s each), how many machines? One GPU answers one question at a time unless you batch.

:::predict Volume triples next year. Which option's monthly cost triples?
---
The API's (it's per query). The local cost barely moves until you hit capacity and need a second machine. That's why the break-even matters more than today's numbers.
:::

:::check
? Which input tokens benefit from prompt caching?
- The user's question
* The repeated prefix: instructions and system prompt
- The model's output
- Retrieved chunks that change each time
> Only an identical prefix can be cached.
:::

:::mistake
Using output tokens at the input price. Output is typically 4-5x more expensive per token; a verbose prompt asking for long answers costs more than it looks.
:::

:::cards
API cost per query? :: (in × price_in + out × price_out) / 1M, cached input cheaper.
Local monthly cost? :: Electricity + hardware / months of life.
Break-even? :: Local monthly ÷ API cost per query.
Capacity at peak? :: ceil(peak qpm × seconds per query / 60).
What triples with volume? :: API cost; local stays flat until capacity.
:::

:::explain Explain to the agency manager what the assistant costs per month, and when that changes.
:::
""",
    "files": [
        lab("day67", "cost_model.py", task=[0, 1]),
    ],
    "tasks": [
        "cost_model.py: query_cost with caching, local_monthly, gpus_needed",
        "break_even and cost_table in USD and TND",
        "Measure your real average tokens per question from the logs and re-run",
    ],
    "done_when": "A monthly cost table for your volume, and the break-even volume.",
    "resources": [{"label": "Anthropic pricing", "url": "https://www.anthropic.com/pricing"},
                  {"label": "Prompt caching", "url": "https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching"}],
    "quiz": [
        {"q": "Which grows linearly with volume?", "options": ["Local electricity", "API cost", "Hardware cost", "Neither"], "answer": 1,
         "explain": "You pay per token."},
        {"q": "Prompt caching reduces the cost of...", "options": ["Output tokens", "The repeated input prefix", "Embeddings", "Latency only"], "answer": 1,
         "explain": "Identical prefixes are billed at a discount."},
    ],
}

DAY68 = {
    "id": "w10d5", "folder": "day68", "date": "2026-12-11", "weekday": "Fri",
    "title": "Failure taxonomy", "minutes": 75,
    "why": "A score says how often it fails. A taxonomy says why, and which single fix removes the most failures.",
    "lesson": r"""
:::hook
12 failures on 50 questions. You start "improving the prompt". But 6 of the 12 never had the right chunk retrieved: no prompt can answer from a chunk it didn't get. One look at the taxonomy would have pointed you at retrieval.
:::

## One cause per failure, in pipeline order

Check causes in the order the pipeline runs, and stop at the first one:

1. **retrieval_miss**: the gold chunk wasn't retrieved.
2. **false_idk**: it was retrieved, but the model said "I don't know".
3. **wrong_answer**: retrieved, answered, wrong.
4. **bad_citation**: right answer, wrong source.
5. **invented_answer**: should have said "I don't know" and didn't.
6. **action_error**: the tool call failed or was wrong.

```python
from collections import Counter
labels = ["retrieval_miss"] * 6 + ["false_idk"] * 3 + ["wrong_answer"] * 2 + ["bad_citation"]
run = 0
for label, n in Counter(labels).most_common():
    run += n
    print(f"{label:15} {n}  cumulative {run / len(labels):.0%}")
```

:::analogy
A car that won't start: check fuel, then battery, then starter, in that order. If there's no fuel, the battery's state doesn't matter yet.
:::

## Slice it

Failure rate by language and by document type. "Derja: 45% failures, French: 12%" or "scanned contracts: 40%, typed rules: 8%" points to a concrete fix (Arabizi handling, OCR quality).

:::predict Top category: false_idk. What do you change?
---
The prompt or the model, not retrieval: the chunk was there and the model refused. Check the IDK instruction (too strict?), the chunk order, and whether the chunk's language confused the model.
:::

:::check
? Why stop at the first matching cause?
- Simpler code
* Each failure gets one label, so counts add up and point at the earliest broken stage
- Rules are slow
- The judge requires it
> Fix upstream first; downstream labels may disappear with it.
:::

:::mistake
Labeling without reading. Read 3 examples of each top category; a wrong rule (say, a gold chunk id that changed after re-indexing) can fill a category with false alarms.
:::

:::cards
First check? :: Was the gold chunk retrieved?
false_idk? :: Chunk retrieved, model said "I don't know".
invented_answer? :: Should have said IDK and answered anyway.
Pareto list? :: Categories by count with cumulative share.
Before trusting labels? :: Read 3 examples per category.
:::

:::explain Explain your top failure category and the one fix you'll try.
:::
""",
    "files": [
        lab("day68", "failure_taxonomy.py", task=[0, 1]),
    ],
    "tasks": [
        "failure_taxonomy.py: classify in pipeline order, taxonomy, pareto",
        "failure_rate_by and examples; run on your best config's dev results",
        "Try the fix for the top category; re-run that config",
    ],
    "done_when": "A Pareto list of failures, 3 examples read per top category, one fix measured.",
    "resources": [],
    "quiz": [
        {"q": "The gold chunk wasn't retrieved and the model said IDK. Label?", "options": ["false_idk", "retrieval_miss", "wrong_answer", "ok"], "answer": 1,
         "explain": "The earliest broken stage wins."},
        {"q": "Top category is retrieval_miss. Best first move?", "options": ["Tune the prompt", "Improve retrieval (chunking, hybrid, k)", "Change the judge", "Add more questions"], "answer": 1,
         "explain": "No prompt can use a chunk it never received."},
    ],
}

DAY69 = {
    "id": "w10d6", "folder": "day69", "date": "2026-12-12", "weekday": "Sat",
    "title": "The final evaluation", "minutes": 180,
    "why": "This is the number you'll put on your CV and in front of Anis. It has to be honest: test set, intervals, targets.",
    "lesson": r"""
:::hook
After a week of tuning on dev, your best config scores 0.89. You run it on the test set for the first time: 0.84. That 5-point drop is normal (you fitted dev a bit) and it's exactly why the test set stayed closed. 0.84 is the number you report.
:::

## Finalists only, once

Take the 2-3 best configs from the dev grid (plus the simplest baseline). Run them on `golden_test.jsonl`. Don't tune after looking; if you must change something, it's a new experiment and the test number is spent.

## Constraints first, then accuracy

Your Week 7 targets have two kinds:
- **Hard constraints**: latency, cost, citation rate. A config that misses them can't ship.
- **The goal**: accuracy. Among configs meeting the constraints, pick the most accurate; tie → cheaper.

```python
configs = {"api-large": (0.88, 0.012), "api-small+rerank": (0.84, 0.004), "local+rerank": (0.84, 0.001)}
max_cost = 0.005
ok = {n: v for n, v in configs.items() if v[1] <= max_cost}
print(max(ok, key=lambda n: (ok[n][0], -ok[n][1])))
```

:::analogy
Hiring under a budget: the best candidate who asks for twice the salary isn't an option. Among those in budget, you take the strongest; between equals, the one who costs less.
:::

:::predict No config meets all hard constraints. What does the report say?
---
Exactly that, with how far each misses, and what would close the gap (a faster model, caching, a GPU). "None meets the targets yet" is a valid, useful result.
:::

:::check
? You see the test results and want to tweak k. What now?
- Tweak and re-run on test
* It's a new experiment: tune on dev, and report the test number already obtained
- Delete the results
- Average both runs
> Every look at test makes it a little more like dev.
:::

:::mistake
Reporting the dev score because it's higher. Interviewers who know evaluation will ask which set it was; "dev" means "optimistic by an unknown amount".
:::

:::cards
Who runs on test? :: 2-3 finalists plus a baseline, once.
Hard constraints? :: Latency, cost, citations: must be met to ship.
Choice rule? :: Best accuracy among configs meeting constraints; tie → cheaper.
Test lower than dev? :: Normal; report the test number.
No config qualifies? :: Say so, with the gaps.
:::

:::explain Explain why your reported score is lower than your best dev score, and why that's good.
:::
""",
    "files": [
        lab("day69", "eval_report.py", task=[0, 1]),
    ],
    "tasks": [
        "eval_report.py: aggregate, missed_targets, choose",
        "results_table with intervals; run the finalists on the test set once",
        "Write down the dev score next to the test score for each finalist",
    ],
    "done_when": "results_table.md from the test set names a recommended config (or says none qualifies).",
    "resources": [],
    "quiz": [
        {"q": "Which config do you recommend?", "options": ["The most accurate overall", "The most accurate among those meeting latency and cost targets", "The cheapest", "The fastest"], "answer": 1,
         "explain": "Constraints first."},
        {"q": "Test score 0.84, dev score 0.89. You report...", "options": ["0.89", "0.84", "The average", "Neither"], "answer": 1,
         "explain": "Test is the honest estimate."},
    ],
}

DAY70 = {
    "id": "w10d7", "folder": "day70", "retest_task": 1, "date": "2026-12-13", "weekday": "Sun",
    "title": "Results report", "minutes": 150,
    "why": "This page is the core of your demo, your README and your interview story. Phase 2's gate is this table.",
    "lesson": r"""
:::hook
Anis's question from the start: "accuracy, cost and latency". Today you answer it on one page: three configs, intervals, a recommendation, the failures behind the numbers, the monthly bill, and what you don't know yet.
:::

## Six sections

1. **Setup**: test set (size, languages), configs, judge, date.
2. **Results**: the table with intervals.
3. **Recommendation**: which, why, the trade-off.
4. **Failures**: top categories with counts and one example each.
5. **Cost**: per month at their volume, and the break-even.
6. **Limitations**: what this evaluation can't tell.

```python
row = {"config": "api-small + rerank", "correct": (0.86, 0.74, 0.95), "p95": 7.4, "usd": 0.0041}
c = row["correct"]
print(f"| {row['config']} | {c[0]:.2f} [{c[1]:.2f}, {c[2]:.2f}] | {row['p95']:.1f} | {row['usd']:.4f} |")
```

:::analogy
A medical test report: what was tested, the values with reference ranges, the conclusion, and "results should be interpreted with the clinical context". Everyone trusts a report more when it states its limits.
:::

## Limitations make it credible

"42 questions → ±10 points", "LLM judge disagrees with me on 1 answer in 10", "one agency's documents". Writing them first means nobody can use them against you.

:::predict The interviewer says "your intervals overlap, so you don't know which is better". Your answer?
---
"Right, on this test set the accuracy difference isn't significant; I chose on the constraints, cost and latency, where the difference is clear. The paired difference interval was [−0.03, 0.15]." That's a strong answer, not a weak one.
:::

:::check
? Which sentence belongs in Limitations?
- "The system works well"
* "The test set has 42 questions, so scores are ±10 points"
- "The API is expensive"
- "Users liked it"
> Concrete limits of the measurement itself.
:::

:::mistake
A recommendation without its trade-off. Every choice gives something up (cost, privacy, latency); naming it shows you understood the decision.
:::

:::cards
Results need? :: Intervals, not just point scores.
Recommendation includes? :: Choice, reason, trade-off.
Failures section? :: Top categories with counts and examples.
Cost in? :: USD and TND per month at their volume.
Why limitations? :: Credibility; they answer objections before they're asked.
:::

:::explain Present your results table to Anis in 60 seconds.
:::
""",
    "files": [
        lab("day70", "results.md", task=0),
    ],
    "tasks": [
        "results.md: table with intervals, recommendation, failures, cost, limitations",
        "Beat the Week 10 boss (8/10)",
        "Retro in notes; push Week 10",
    ],
    "done_when": "results.md committed and 8/10 on the boss.",
    "resources": [],
    "quiz": [
        {"q": "Best Limitations bullet?", "options": ["'More work needed'", "'42 test questions: about ±10 points'", "'The model is good'", "'Results are promising'"], "answer": 1,
         "explain": "Specific, about the measurement."},
    ],
    "retest": [
        {"q": "The experiment grid runs on...", "options": ["Test", "Dev", "Production", "Both always"], "answer": 1,
         "explain": "Tune on dev; test once."},
        {"q": "Why put the data version in the run key?", "options": ["Longer keys", "Never mix results from different question sets", "Sorting", "Speed"], "answer": 1,
         "explain": "Comparable numbers need the same data."},
        {"q": "A judge picks A in both orders. Outcome?", "options": ["A wins", "B wins", "Tie", "Error"], "answer": 2,
         "explain": "Position bias, not preference."},
        {"q": "Win rate with 2 wins, 1 loss, 1 tie?", "options": ["0.5", "0.625", "0.75", "0.67"], "answer": 1,
         "explain": "(2 + 0.5) / 4."},
        {"q": "The paired difference interval is [−0.02, 0.09]. Conclusion?", "options": ["A better", "B better", "Not significant", "Invalid"], "answer": 2,
         "explain": "0 is inside."},
        {"q": "Paired bootstrap resamples...", "options": ["Each config separately", "Question indexes, shared by both configs", "Judges", "Models"], "answer": 1,
         "explain": "Pairs stay together."},
        {"q": "Which cost grows linearly with volume?", "options": ["API", "Local hardware", "Electricity at idle", "None"], "answer": 0,
         "explain": "Per-token billing."},
        {"q": "Gold chunk not retrieved, model said IDK. Label?", "options": ["false_idk", "retrieval_miss", "invented_answer", "ok"], "answer": 1,
         "explain": "Earliest broken stage."},
        {"q": "Choosing the final config:", "options": ["Highest accuracy", "Highest accuracy among configs meeting hard constraints", "Cheapest", "Newest model"], "answer": 1,
         "explain": "Constraints first."},
        {"q": "Dev 0.89, test 0.84. Report...", "options": ["0.89", "0.84", "0.865", "Both, dev first"], "answer": 1,
         "explain": "Test is the honest estimate."},
    ],
}

WEEK10 = {
    "n": 10, "phase": "Phase 2", "title": "Evaluate", "dates": "Dec 7-13",
    "goal": "Two configurations compared on accuracy, latency, cost.",
    "gate": "Results table",
    "days": [DAY64, DAY65, DAY66, DAY67, DAY68, DAY69, DAY70],
}
