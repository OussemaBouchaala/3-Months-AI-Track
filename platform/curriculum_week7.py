"""Week 7: Scope the project (Nov 16-22, 2026)."""
from lab_files import lab

DAY43 = {
    "id": "w7d1", "folder": "day43", "date": "2026-11-16", "weekday": "Mon",
    "title": "Choosing the project", "minutes": 75,
    "why": "Phase 2 is six weeks on one project. Picking it with criteria, not excitement, is the first engineering decision.",
    "lesson": r"""
:::hook
Two options. A "smart contract analyzer" sounds impressive, but you have no contracts and no user. A "document assistant for an agency" sounds ordinary, but a real agent will test it every day. In six weeks, the second one has numbers, feedback and a demo. The first has a README.
:::

## Criteria before options

Write what matters **before** scoring, or you'll pick weights that make your favorite win. For a portfolio project in Tunisia:
- **Real user**: someone will use it and tell you what's wrong.
- **Data access**: you can get the documents this week, legally.
- **Arabic**: it uses what you learned in Phase 1.
- **Action**: at least one tool that does something (Week 5).
- **Demo**: it can be shown in 3 to 5 minutes.

```python
weights = {"real_user": 3, "data_access": 3, "arabic": 2, "action": 2, "demo": 1}
options = {"Agency assistant": [4, 4, 4, 5, 4], "Contract analyzer": [2, 1, 3, 2, 4]}
total = sum(weights.values())
for name, scores in options.items():
    print(name, round(sum(w / total * s for w, s in zip(weights.values(), scores)), 2))
```

:::analogy
Buying a flat: you list "close to work, 2 rooms, under 900 TND" before visiting. Otherwise the one with a nice balcony wins, and you commute 90 minutes a day.
:::

## Is the winner solid?

If moving one weight by 1 changes the winner, your choice is a coin flip. That's a **sensitivity** check. A fragile result means: talk to a user before deciding, because the data you lack decides it.

:::predict Your favorite option scores 3.9, the other 3.8, and lowering "data access" by 1 flips them. What do you do?
---
Find out about data access for real (ask for the documents today). The matrix told you exactly which unknown matters; don't decide until it's known.
:::

:::check
? Which criterion most often kills student projects in week 3 of building?
- Model choice
* No access to real data
- Framework choice
- UI design
> You can swap models in an afternoon. You can't invent a client's documents.
:::

:::mistake
Scoring after choosing. If you already know the winner, the matrix is decoration. Write the weights first, then score each option honestly, then look at the result.
:::

:::cards
Decision matrix? :: Options scored on weighted criteria.
Why normalize weights? :: So scores stay on the 1-5 scale and are comparable.
Sensitivity check? :: Nudge each weight; see if the winner changes.
Fragile winner? :: Resolve the key unknown before deciding.
Strongest criterion for a portfolio project? :: A real user with real data.
:::

:::explain Explain to a friend why you picked your Phase 2 project, using the matrix and one number.
:::
""",
    "files": [
        lab("day43", "decision_matrix.py", task=[0, 1]),
    ],
    "tasks": [
        "decision_matrix.py: weights, scores, ranking",
        "Sensitivity check; resolve the unknown if the winner is fragile",
        "Write your project in one sentence in your notes",
    ],
    "done_when": "One project chosen, and you can say which criterion decided it.",
    "resources": [],
    "quiz": [
        {"q": "When should criteria weights be set?", "options": ["After scoring the options", "Before scoring", "After the project", "Never"], "answer": 1,
         "explain": "Otherwise you tune weights to fit your favorite."},
        {"q": "Nudging one weight flips the winner. That means...", "options": ["The matrix is broken", "The choice is fragile; resolve that unknown first", "Pick at random", "Add more criteria"], "answer": 1,
         "explain": "The sensitivity check tells you what to find out."},
    ],
}

DAY44 = {
    "id": "w7d2", "folder": "day44", "date": "2026-11-17", "weekday": "Tue",
    "title": "Interviewing the user", "minutes": 75,
    "why": "Your test set, your targets and your scope all come from one conversation with the person who'll use the system.",
    "lesson": r"""
:::hook
You ask the agent: "Would an AI assistant help you?" She says "Yes, sure!" You learned nothing. You ask: "What did you answer on WhatsApp yesterday? Show me." Now you have 10 real questions, 3 in Derja, and a scanned contract nobody can search.
:::

## Ask about the past, not the future

People are bad at predicting what they'd use, and good at describing what they did. Good questions:
- "Walk me through the last time a client asked about fees."
- "Where did you look? How long did it take?"
- "Can you show me the message and the document?"
- "What happens when you get it wrong?"

:::analogy
A doctor doesn't ask "would you like a medicine?". They ask "where does it hurt, since when, how often?". The diagnosis comes from symptoms, not wishes.
:::

## Collect numbers and artifacts

Every pain point gets a number if possible: "about 40 a day", "5 to 10 minutes", "twice last month". Those numbers become your targets on Thursday. Every question gets written **in their words and language**: those become your golden set on Saturday.

```python
pain = [("repeated questions", 40, "per day"), ("time to find a clause", 7.5, "minutes"), ("double bookings", 2, "per month")]
for what, n, unit in pain:
    print(f"{what}: {n} {unit}")
print("minutes saved per day if half the repeated questions take 1 min instead of 3:", 40 / 2 * (3 - 1))
```

:::predict The user says "it should handle everything". What's your next question?
---
"What came up most this week?" or "What took the longest yesterday?". Turn "everything" into the top 3 concrete cases; those are your first version.
:::

:::check
? Which interview question gives the most useful answer?
- "Would you use an AI chatbot?"
- "What features do you want?"
* "Show me the last three client questions you answered, and how you found the answers"
- "Do you like technology?"
> Real past behavior, with artifacts you can test on.
:::

:::mistake
Pitching your solution during the interview. As soon as you describe your idea, they start agreeing with you. Listen first; show nothing until the notes are written.
:::

:::cards
Ask about? :: What they did last time, not what they'd like.
Every pain point gets? :: A number: how often, how long, how much.
Their questions are written? :: Word for word, in their language.
Ask to see? :: Real documents and messages.
When to pitch your idea? :: After the notes are written, if at all.
:::

:::explain Explain why "would you use it?" is a bad interview question.
:::
""",
    "files": [
        lab("day44", "interview.md", task=[0, 1]),
    ],
    "tasks": [
        "Book and run a 30-minute interview with a real user",
        "interview.md: workflow, pain points with numbers, 8+ real questions",
        "Ask for written permission to use the documents",
    ],
    "done_when": "Notes written with 8 real questions and at least one number per pain point.",
    "resources": [{"label": "The Mom Test (summary)", "url": "https://www.momtestbook.com/"}],
    "quiz": [
        {"q": "Best interview question?", "options": ["Would you pay for this?", "Walk me through the last time this happened", "Do you like AI?", "What features do you want?"], "answer": 1,
         "explain": "Past behavior is reliable; predictions aren't."},
        {"q": "Why write their questions word for word?", "options": ["Politeness", "They become your test set, in their real language", "Legal reasons", "To translate them"], "answer": 1,
         "explain": "Your eval must look like real traffic."},
    ],
}

DAY45 = {
    "id": "w7d3", "folder": "day45", "notes_task": 2, "date": "2026-11-18", "weekday": "Wed",
    "title": "Personal data first", "minutes": 75,
    "why": "Real documents contain phone numbers, ID numbers and bank details. Masking them before anything else is both law and trust.",
    "lesson": r"""
:::hook
You paste a client's lease into an API prompt to test your RAG. It contains a CIN, a phone number and a RIB. That text is now on a server abroad, maybe in logs. Tunisia's data protection law (loi organique 2004-63) and the client's trust both say: that shouldn't happen.
:::

## What counts as personal data here

| Kind | Example | Pattern |
|---|---|---|
| Phone | +216 98 123 456 | 8 digits starting 2-9, optional +216 |
| CIN | 09876543 | 8 digits starting 0 or 1 |
| RIB | 08 006 0001234567890 12 | 20 digits |
| Email | salma@gmail.com | standard regex |
| Names | Salma Ben Ali | known list (clients, owners) |

## Mask consistently

`[PHONE_1]` everywhere the same number appears, so the text still makes sense: "[NAME_1] called from [PHONE_1], then [PHONE_1] again". Keep the mapping **locally** so you can show the real value to the agent.

```python
import re
mapping = {}
def mask(m):
    v = m.group()
    key = next((k for k, x in mapping.items() if x == v), f"[PHONE_{len(mapping) + 1}]")
    mapping[key] = v
    return key
print(re.sub(r"(?<!\d)[2-9]\d{7}(?!\d)", mask, "Call 98123456, or 22333444, or 98123456."), mapping)
```

:::analogy
A hospital's research files: patients become "Patient 17". Researchers can study the cases; only the hospital holds the list that maps 17 back to a name.
:::

:::predict A RIB contains "60001234". Your phone regex runs first. What happens?
---
Part of the RIB gets masked as a phone, and the rest of the RIB is left visible. Run the longest, most specific patterns first (RIB), and skip matches that overlap one already found.
:::

## Where scrubbing sits

Before indexing, before any API call, before logging. Not after. A log line with a phone number is a leak, even if the answer was fine.

:::check
? Why keep the mapping instead of just deleting the PII?
- To save space
* So the agent can see the real values locally, while APIs and logs only see placeholders
- The law requires it
- For embeddings
> Mask for machines outside, restore for the human inside.
:::

:::mistake
`\d{8}` for phones. It matches inside longer numbers, CINs, dates like 20251118, and prices. Use lookarounds `(?<!\d)...(?!\d)` and the first-digit rule.
:::

:::cards
CIN vs phone? :: Both 8 digits; CIN starts with 0/1, mobile phones with 2-9.
Why patterns in order? :: Long ones (RIB) first, so short ones don't cut them.
Same value twice? :: Same placeholder.
Where to scrub? :: Before indexing, API calls and logs.
Who sees real values? :: Only the agent, through local restore.
:::

:::explain Explain to the agency manager what happens to a client's phone number in your system.
:::
""",
    "files": [
        lab("day45", "pii_scrub.py", task=[0, 1]),
    ],
    "tasks": [
        "pii_scrub.py: PHONE and CIN regexes, find_pii with priorities",
        "scrub, scrub_names, restore with a shared mapping",
        "Run it on 5 real messages; note anything that slips through",
    ],
    "done_when": "Five real messages come out with no phone, CIN, RIB or email visible.",
    "resources": [{"label": "INPDP (Tunisian data protection authority)", "url": "http://www.inpdp.nat.tn/"}],
    "quiz": [
        {"q": "Where should PII scrubbing run?", "options": ["After the answer", "Before indexing, API calls and logging", "Only in the UI", "Nowhere locally"], "answer": 1,
         "explain": "Once it has left, you can't take it back."},
        {"q": "Why match the RIB pattern before phones?", "options": ["It's rarer", "Phones would match pieces of it", "Alphabetical order", "Speed"], "answer": 1,
         "explain": "Specific and long first, then skip overlaps."},
    ],
}

DAY46 = {
    "id": "w7d4", "folder": "day46", "date": "2026-11-19", "weekday": "Thu",
    "title": "Success targets", "minutes": 75,
    "why": "Without numbers agreed in advance, every result looks fine. Targets make 'done' measurable.",
    "lesson": r"""
:::hook
Week 10, your results: 78% correct, p95 of 8 seconds, 0.004 USD a question. Is that good? If you didn't write targets now, you'll decide after seeing the numbers, and you'll always decide "yes".
:::

## Four numbers

| Metric | From the interview | Target |
|---|---|---|
| Answer correct | "if it's wrong twice, I stop using it" | ≥ 80% |
| Correct citation | "I need to show the client the clause" | ≥ 90% |
| p95 latency | "10 seconds, while the client waits" | ≤ 10 s |
| Cost per question | "30 TND a month" for ~2,000 questions | ≤ 0.005 USD |

Each target **comes from something the user said**. That's what makes it defensible.

## Percentiles, not averages

Latency is skewed: most answers in 3 seconds, a few in 25. The mean hides the slow ones; p95 says "19 out of 20 users wait at most this long".

```python
import math
lat = [2.1, 2.4, 2.2, 3.0, 2.8, 2.5, 2.9, 3.1, 2.6, 24.0]
s = sorted(lat)
p95 = s[math.ceil(0.95 * len(s)) - 1]
print("mean", round(sum(lat) / len(lat), 1), "p50", s[math.ceil(0.5 * len(s)) - 1], "p95", p95)
```

:::analogy
A bus company that says "average delay 4 minutes" while one bus in ten is 40 minutes late. Riders remember the 40.
:::

:::predict 2,000 questions a month, budget 30 TND (about 9.5 USD). Max cost per question?
---
About 0.0048 USD. With 2,000 input tokens and 200 output tokens per question, that rules out the most expensive models, and points to a small API model or a local one. The target already shapes the architecture.
:::

:::check
? Why p95 latency rather than the mean?
- It's easier to compute
* The slow tail is what users notice; the mean hides it
- The mean is always higher
- APIs report it
> Users experience the tail.
:::

:::mistake
Targets nobody can measure ("answers should be helpful"). If you can't compute it from your golden set and logs, it's a wish, not a target.
:::

:::cards
Where do targets come from? :: The user's own words, turned into numbers.
p95? :: 95% of requests are at or below this value.
Cost per question? :: (in tokens x price in + out tokens x price out) / 1M.
When to set targets? :: Before building and before seeing results.
Unmeasurable target? :: A wish; rewrite it as a number.
:::

:::explain Explain to the user why you'll report p95 latency and not the average.
:::
""",
    "files": [
        lab("day46", "targets.py", task=[0, 1]),
    ],
    "tasks": [
        "targets.py: percentile, cost per query, summarize",
        "check_targets and report; TARGETS from your interview",
        "Write next to each target the sentence of the user it comes from",
    ],
    "done_when": "Four targets, each traced to the interview, and a checker that prints OK / MISS.",
    "resources": [],
    "quiz": [
        {"q": "Latencies 2,2,3,3,3,3,3,3,3,30 s. Which describes the user experience best?", "options": ["Mean 5.5 s", "p95 = 30 s plus p50 = 3 s", "Min 2 s", "Mode 3 s"], "answer": 1,
         "explain": "Typical case plus the tail."},
        {"q": "A good target is...", "options": ["'Fast and accurate'", "'p95 under 10 s on the golden set'", "'Better than ChatGPT'", "'Users are happy'"], "answer": 1,
         "explain": "Measurable, with a dataset."},
    ],
}

DAY47 = {
    "id": "w7d5", "folder": "day47", "notes_task": 2, "date": "2026-11-20", "weekday": "Fri",
    "title": "Architecture on one page", "minutes": 75,
    "why": "A diagram and a few written decisions save days of rework, and they're what interviewers ask you to draw.",
    "lesson": r"""
:::hook
"Draw your system on the whiteboard." Every AI engineering interview has this moment. If you designed it on paper first, you draw it in two minutes and spend the rest of the time on the interesting decisions.
:::

## Components and arrows

Most RAG products share one shape:

```python
flow = ["Documents", "Ingestion (parse, OCR, PII scrub, chunk)", "Index (pgvector + BM25)",
        "Retriever (hybrid + rerank)", "LLM (answer with citations)", "API", "UI"]
print("\n  -> ".join(flow))
```

Plus the action path: UI → API → tool → external system, with confirmation. Your diagram is this, with your real names.

:::analogy
A metro map: not to scale, no street names, but every station and every connection. You can plan a trip from it in seconds. That's the level of detail you want.
:::

## Mermaid: diagrams as text

GitHub, Bench and many docs tools render ` ```mermaid ` blocks. Text means it lives in the repo, gets reviewed in PRs, and stays up to date.

## Decisions: "X instead of Y, because Z"

- "Local embeddings **instead of** an embeddings API, **because** the documents contain client data."
- "Hybrid search **instead of** vectors only, **because** Phase 1 showed +7 points on names and dates."

Each decision has an alternative and a reason. That sentence shape is exactly how you answer "why did you…?" in an interview.

:::predict You can't write a "because" for a decision. What does that mean?
---
You haven't made the decision, you've defaulted to it. Either find the reason (a constraint, a number) or mark it as an open question to test in Week 10.
:::

:::check
? What belongs in the "Storage" section?
- The code of the indexer
* What is stored where, and what is deliberately NOT stored (like PII)
- The database password
- The Docker version
> Data is where privacy promises are kept or broken.
:::

:::mistake
A diagram with 25 boxes. If it doesn't fit on one screen, nobody reads it. Group: "Ingestion" is one box, its steps go in the text.
:::

:::cards
Mermaid? :: Text that renders as a diagram (flowchart LR, A --> B).
Database node in Mermaid? :: A[(Name)]
A good decision sentence? :: X instead of Y, because Z.
Diagram size? :: Fits on one screen, 6-10 boxes.
Risks section? :: What can fail, and what you'll do about it.
:::

:::explain Explain your architecture out loud in 90 seconds, following the arrows.
:::
""",
    "files": [
        lab("day47", "architecture.md", task=[0, 1]),
    ],
    "tasks": [
        "Components, data flow and storage",
        "Mermaid diagram (5+ arrows), two decisions, two risks",
        "Practice drawing it from memory in 2 minutes",
    ],
    "done_when": "architecture.md renders on GitHub with its diagram, and you can draw it from memory.",
    "resources": [{"label": "Mermaid flowchart syntax", "url": "https://mermaid.js.org/syntax/flowchart.html"},
                  {"label": "mermaid.live editor", "url": "https://mermaid.live"}],
    "quiz": [
        {"q": "Why Mermaid over an image?", "options": ["Prettier", "It's text: versioned, reviewed, easy to update", "Faster to render", "Required by GitHub"], "answer": 1,
         "explain": "Diagrams as code stay in sync with the code."},
        {"q": "Which decision is well written?", "options": ["'We use pgvector'", "'pgvector instead of Pinecone, because data must stay on the office PC'", "'pgvector is the best'", "'Database: yes'"], "answer": 1,
         "explain": "Alternative and reason."},
    ],
}

DAY48 = {
    "id": "w7d6", "folder": "day48", "date": "2026-11-21", "weekday": "Sat",
    "title": "The golden set", "minutes": 180,
    "why": "Every number you report in Weeks 8-10 is computed on this set. If it's thin or biased, every number lies.",
    "lesson": r"""
:::hook
Week 10: "92% correct!" Then the agent tries it and it fails on every Derja question. Your golden set had 25 French questions and one in Derja. The number was honest about the set; the set wasn't honest about the users.
:::

## What goes in

- The interview's questions, **word for word**.
- Variations: the same need in other languages the users write in.
- **idk** items: questions the documents can't answer. The right output is "I don't know".
- **action** items: requests that need the tool ("book a visit Saturday 10am").
- At least 3 items per category, so a category's score isn't one coin flip.

```python
items = [{"lang": "fr", "type": "answer"}] * 12 + [{"lang": "derja", "type": "answer"}] * 3 + [{"lang": "en", "type": "idk"}] * 1
from collections import Counter
print(Counter(i["lang"] for i in items), Counter(i["type"] for i in items))
```

:::analogy
A driving test only on empty roads in daylight: you pass, and crash the first rainy night. The test has to include rain, night and roundabouts, in proportion to real driving.
:::

## Dev and test, once

Split now, stratified by category, with a seed. **Dev** is for tuning (prompts, k, chunk size). **Test** is opened once, in Week 10, for the final number. If you tune on test, the final number is optimistic and you won't know by how much.

:::predict You have 1 question in the "pets" category. With a 30% test share, where does it go?
---
In dev (round(0.3) = 0). With only one item, the test set has no "pets" question at all. That's why `gaps` flags categories with fewer than 3 items: write more before splitting.
:::

:::check
? Why include questions the documents can't answer?
- To lower the score
* To measure whether the system says "I don't know" instead of inventing
- To test the UI
- They are easier
> A system that always answers looks great until the first invented clause.
:::

:::mistake
Writing all the questions yourself, in your style. Your users write shorter, with typos, in Derja and Arabizi. Use their words; add your variations after.
:::

:::cards
idk item? :: A question the documents don't answer; correct output is "I don't know".
Why stratify the split? :: Every category appears in both dev and test.
Dev is for? :: Tuning.
Test is for? :: The final number, opened once.
Minimum per category? :: About 3, or the category score is noise.
:::

:::explain Explain to your user why you'll keep some of their questions hidden until Week 10.
:::
""",
    "files": [
        lab("day48", "golden_set.py", task=[0, 1]),
    ],
    "tasks": [
        "golden_set.py: 20+ items with validation, dedupe and coverage",
        "Stratified dev/test split and gaps; commit both files",
        "Show 5 items to your user and ask: is this how clients ask?",
    ],
    "done_when": "golden_dev.jsonl and golden_test.jsonl committed, no gaps, user checked a sample.",
    "resources": [],
    "quiz": [
        {"q": "You tune prompts on the test set. Your final number is...", "options": ["Accurate", "Optimistic", "Pessimistic", "Unaffected"], "answer": 1,
         "explain": "You've fitted to the exam."},
        {"q": "Why a seed for the split?", "options": ["Speed", "Same split every run", "Better accuracy", "Required by JSONL"], "answer": 1,
         "explain": "A moving test set makes runs incomparable."},
    ],
}

DAY49 = {
    "id": "w7d7", "folder": "day49", "retest_task": 1, "date": "2026-11-22", "weekday": "Sun",
    "title": "The scope document", "minutes": 150,
    "why": "One signed page turns six weeks of 'maybe also...' into a plan you can finish.",
    "lesson": r"""
:::hook
Week 9, the manager says: "Could it also answer clients on WhatsApp directly?" Without a scope document you say yes, and lose a week. With one, you say: "That's out of scope for this version, it's on the list for the next."
:::

## One page, eight sections

1. **Problem** in the user's terms, with a number.
2. **User**: who, how often, on what.
3. **In scope**: what version 1 does.
4. **Out of scope**: what it doesn't.
5. **Data**: what, how much, with whose permission.
6. **Success metrics**: the four targets.
7. **Timeline**: Weeks 8-12, one line each.
8. **Sign-off**: who agreed, when.

:::analogy
A builder's quote: rooms, materials, price, dates, and what's not included ("painting not included"). Both sides sign before the first wall goes up.
:::

## Out of scope is a feature

```python
requests = ["WhatsApp bot", "price estimates", "book visits", "voice notes"]
in_scope = {"book visits"}
for r in requests:
    print(f"{r:16} -> {'this version' if r in in_scope else 'later (out of scope)'}")
```

The list protects your time, and it shows judgment: knowing what not to build is a senior skill.

:::predict Your timeline has "Week 10: evaluation" but no golden set exists yet. What's wrong?
---
Nothing now: you built it yesterday. That's the point of doing Week 7 in this order: interview → targets → golden set → scope. Each document feeds the next.
:::

:::check
? Who should sign off the scope?
- You alone
* The user or the data owner
- A random developer
- Nobody, it's internal
> Agreement from the person whose problem it is, and whose data you use.
:::

:::mistake
A scope with no out-of-scope list. Everything is implicitly in scope, and every new idea becomes your problem.
:::

:::cards
Problem statement includes? :: The user's terms and a number.
Out of scope protects? :: Your timeline.
Success metrics come from? :: targets.py, from the interview.
Sign-off? :: Name or role plus date.
Order of Week 7? :: Choose, interview, PII, targets, architecture, golden set, scope.
:::

:::explain Explain your project in 30 seconds: problem, user, what it does, how you'll know it works.
:::
""",
    "files": [
        lab("day49", "scope.md", task=0),
    ],
    "tasks": [
        "scope.md: one page, signed off",
        "Beat the Week 7 boss (8/10)",
        "Retro in notes; push Week 7 to GitHub",
    ],
    "done_when": "Scope signed off and 8/10 on the boss.",
    "resources": [],
    "quiz": [
        {"q": "Why write an out-of-scope list?", "options": ["Bureaucracy", "To protect the timeline from new requests", "To lower expectations", "The law"], "answer": 1,
         "explain": "Every 'also' has a cost."},
    ],
    "retest": [
        {"q": "Decision matrix weights should be set...", "options": ["After scoring", "Before scoring", "By the model", "At random"], "answer": 1,
         "explain": "Otherwise they get tuned to your favorite."},
        {"q": "A winner that flips when one weight moves by 1 is...", "options": ["Robust", "Fragile: resolve that unknown first", "Wrong", "Optimal"], "answer": 1,
         "explain": "Sensitivity tells you what to find out."},
        {"q": "Best interview question?", "options": ["Would you use an AI?", "Show me the last questions you answered and how", "What features do you want?", "Is AI useful?"], "answer": 1,
         "explain": "Past behavior with artifacts."},
        {"q": "A Tunisian CIN vs a mobile number: how do you tell them apart?", "options": ["Length", "First digit: 0/1 for CIN, 2-9 for phones", "Spaces", "You can't"], "answer": 1,
         "explain": "Both are 8 digits."},
        {"q": "Where should PII be masked?", "options": ["In the UI", "Before indexing, API calls and logs", "After answering", "Only in logs"], "answer": 1,
         "explain": "Before it leaves your machine."},
        {"q": "Why report p95 latency?", "options": ["Easier", "It shows the slow tail users feel", "It's always lower", "APIs require it"], "answer": 1,
         "explain": "The mean hides the tail."},
        {"q": "A good decision in architecture.md reads...", "options": ["'We use X'", "'X instead of Y, because Z'", "'X is best'", "'X, Y and Z'"], "answer": 1,
         "explain": "Alternative and reason."},
        {"q": "Why include 'idk' items in the golden set?", "options": ["Variety", "To measure if the system admits it doesn't know", "To lower scores", "For the UI"], "answer": 1,
         "explain": "Inventing answers is the worst failure."},
        {"q": "The golden test split is used...", "options": ["For tuning every day", "Once, for the final number", "Never", "For training"], "answer": 1,
         "explain": "Tune on dev."},
        {"q": "Who signs off the scope?", "options": ["You", "The user or data owner", "GitHub", "Nobody"], "answer": 1,
         "explain": "The person whose problem and data it is."},
    ],
}

WEEK7 = {
    "n": 7, "phase": "Phase 2", "title": "Scope the project", "dates": "Nov 16-22",
    "goal": "One-page problem statement with a real user and data.",
    "gate": "Signed-off scope",
    "days": [DAY43, DAY44, DAY45, DAY46, DAY47, DAY48, DAY49],
}
