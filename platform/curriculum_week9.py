"""Week 9: Build II, tool calling and a usable UI (Nov 30-Dec 6, 2026)."""
from lab_files import lab

DAY57 = {
    "id": "w9d1", "folder": "day57", "date": "2026-11-30", "weekday": "Mon",
    "title": "The real action", "minutes": 75,
    "why": "Answering is helpful; acting is valuable. It's also where a mistake costs real money or a real appointment.",
    "lesson": r"""
:::hook
The agent types "réserver L12 samedi 10h pour Amel". The model fills the tool call, but reads "samedi" as next week's Saturday, not this one. If the booking runs immediately, Amel shows up on the wrong day. If the agent first reads "Réserver une visite du bien L12 le samedi 12/12 à 10:00", they catch it in one second.
:::

## Propose, preview, confirm

1. **Propose**: validate the arguments (Pydantic). Invalid? Say what's wrong; don't guess.
2. **Preview**: one plain sentence in the user's language, with the exact date, not "samedi".
3. **Confirm**: a human click. Only then execute.

```python
from datetime import datetime
DAYS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
when = datetime(2026, 12, 12, 10, 0)
print(f"Réserver une visite du bien L12 le {DAYS[when.weekday()]} {when:%d/%m} à {when:%H:%M} pour Amel.")
```

:::analogy
A pharmacist reading back a prescription: "Amoxicillin 500, three times a day, seven days, correct?". The doctor's handwriting was the model's output; the read-back is the preview.
:::

## Once, and not forever

- **Idempotent**: same tool + same args → same action id. A double click doesn't book twice.
- **Expiry**: a pending action older than 10 minutes is dropped. Yesterday's forgotten preview shouldn't run today.
- **Failure stays pending**: if the API returns 409, the agent can fix and retry, nothing is lost.
- **Audit log**: who proposed what, when, and what happened.

:::predict The agent confirms, the API times out, and the agent clicks again. What should happen?
---
If the first call actually went through, the second click returns "already_done" with the same result (if your desk recorded it), or the API's own idempotency key prevents a duplicate. Either way: one visit. That's why Week 5's idempotency key and today's action id both exist.
:::

:::check
? Why show the exact date ("samedi 12/12") instead of the user's words ("samedi")?
- It's shorter
* The preview must show what will actually run, so the human can catch the model's interpretation errors
- Pydantic requires it
- For the audit log
> Confirming the user's own words confirms nothing.
:::

:::mistake
A confirm step that the model can trigger itself (a "confirm" tool). Then the model proposes and confirms in one loop, and the human never sees anything. Confirmation is a UI button, outside the model's reach.
:::

:::cards
Three steps of a safe action? :: Propose (validate), preview (plain sentence), confirm (human).
Same request twice? :: Same action id, executed once.
Pending too long? :: Expired after the TTL.
API failure on confirm? :: Status failed; the action stays pending for a retry.
Who confirms? :: A human click, never the model.
:::

:::explain Explain to the agency manager why the assistant asks "Confirmer ?" before booking.
:::
""",
    "files": [
        lab("day57", "action_tool.py", task=[0, 1]),
    ],
    "tasks": [
        "action_tool.py: action_id, preview, propose with validation",
        "confirm (once, expiry, failure), cancel, audit log",
        "Run against the day31 visits API: two confirms, one booking",
    ],
    "done_when": "Two confirmations of the same action create one visit, and the audit shows both.",
    "resources": [],
    "quiz": [
        {"q": "The preview should show...", "options": ["The user's exact words", "What will actually be executed, with exact values", "The JSON", "Nothing"], "answer": 1,
         "explain": "So the human can catch misinterpretations."},
        {"q": "A pending action is 2 hours old when confirmed. Best behavior?", "options": ["Execute it", "Expired: ask again", "Execute twice", "Delete the audit"], "answer": 1,
         "explain": "Old previews may no longer match the situation."},
    ],
}

DAY58 = {
    "id": "w9d2", "folder": "day58", "notes_task": 2, "date": "2026-12-01", "weekday": "Tue",
    "title": "From ask to chat", "minutes": 75,
    "why": "Agents ask follow-ups. A chat that forgets the previous question answers the wrong thing confidently.",
    "lesson": r"""
:::hook
"Combien de caution ?" → "Deux mois [1]." Then: "et avec un chat ?". Searched alone, "et avec un chat" retrieves the pets rule, but not the deposit rule, so the model can't say "two and a half months". The follow-up needs the previous question.
:::

## Sessions and short history

Each conversation gets a `session_id`. The server keeps its last few messages (6 is plenty) and sends them to the model. More history = more tokens = more cost and latency, and old turns confuse more than they help.

## Rewrite follow-ups for retrieval

The model can read the history; **the retriever can't**. For short follow-ups, search with the previous user question joined to the new message.

```python
history = [("user", "Combien de caution ?"), ("assistant", "Deux mois [1].")]
msg = "et avec un chat ?"
last = next(m for r, m in reversed(history) if r == "user")
query = f"{last} {msg}" if len(msg.split()) <= 5 else msg
print("search:", query)
```

A better version asks the model to rewrite the question ("query rewriting"), at the cost of one more call. Start with the rule; measure; upgrade if needed.

:::analogy
A phone call transferred between colleagues. "And for a cat?" means nothing to the second colleague unless the first one says "she's asking about the deposit".
:::

## Routing

Question → RAG. Action words (réserver, book, نحجز, nheb nchouf) → the action desk. Missing details → ask for them instead of guessing.

:::predict A user writes "nheb nchouf l'appart" (I want to see the flat) with no date. What should the chat do?
---
Route to action, find no listing or date, and ask "Pour quel bien, quel jour et quelle heure ?". Guessing a date is how wrong bookings happen.
:::

:::check
? Why does the retriever need the rewritten query when the model already gets the history?
- It doesn't
* The retriever only sees the query text; without context it fetches the wrong chunks, and the model can't cite what wasn't retrieved
- To save tokens
- For the UI
> Retrieval happens before the model reads anything.
:::

:::mistake
Keeping the whole history forever. Long sessions get slow and expensive, and an old topic leaks into new answers. Trim to the last few messages.
:::

:::cards
session_id? :: Identifies one conversation; created if missing.
How much history? :: The last ~6 messages.
Follow-up rewrite? :: Join a short message to the previous user question for retrieval.
Missing action details? :: Ask, don't guess.
Routing rule? :: Action words → desk, otherwise → RAG.
:::

:::explain Explain why "et avec un chat ?" fails without query rewriting.
:::
""",
    "files": [
        lab("day58", "chat_endpoint.py", task=[0, 1]),
    ],
    "tasks": [
        "chat_endpoint.py: route, trim_history, retrieval_query",
        "/chat and /chat/confirm with sessions and the action desk",
        "Try 3 real follow-ups from your interview; note which still fail",
    ],
    "done_when": "A 4-message conversation with a follow-up and a booking works through /chat.",
    "resources": [],
    "quiz": [
        {"q": "Why trim the history?", "options": ["Privacy only", "Cost, latency, and old topics confusing new answers", "FastAPI limits", "SQLite limits"], "answer": 1,
         "explain": "Every message is re-sent on every turn."},
        {"q": "'et pour un chat ?' should be searched as...", "options": ["As is", "Joined to the previous user question", "Translated", "Ignored"], "answer": 1,
         "explain": "The retriever has no memory."},
    ],
}

DAY59 = {
    "id": "w9d3", "folder": "day59", "date": "2026-12-02", "weekday": "Wed",
    "title": "Streaming answers", "minutes": 75,
    "why": "Users judge speed by the first word, not the last. Streaming makes a 6-second answer feel immediate.",
    "lesson": r"""
:::hook
Same answer, same 6 seconds. Version A: blank screen, then the whole text. Version B: the first words after 0.6 s, the rest flowing in. Users rate B as much faster. Nothing got faster except the **time to first token**.
:::

## Server-Sent Events

The simplest streaming over HTTP: the response stays open and the server writes events.

```python
def sse(data, event=None):
    head = f"event: {event}\n" if event else ""
    return head + "".join(f"data: {line}\n" for line in data.split("\n")) + "\n"
print(sse("La ", "token") + sse("caution", "token") + sse("[DONE]", "done"), end="")
```

- One event per token (or per few tokens).
- Then a **sources** event (citations are known at the end).
- Then **done**, so the client knows to stop.
- On failure mid-stream: an **error** event. The HTTP status is already 200, so errors must travel inside the stream.

:::analogy
A live sports text commentary versus the match report the next morning. Same information, but you're following along as it happens.
:::

## SSE vs WebSockets

SSE is one-way (server → client), plain HTTP, reconnects automatically, works through most proxies. WebSockets are two-way and more complex. A chat answer only flows one way: SSE is enough.

:::predict Your stream works locally but arrives all at once behind Nginx. Why?
---
The proxy buffers the response. Send `X-Accel-Buffering: no` (and `Cache-Control: no-cache`) so it passes events through as they come.
:::

:::check
? Why send sources as a separate event at the end?
- They're secret
* The citations are only known once the answer is complete
- SSE can't send JSON
- To save bandwidth
> Tokens first, metadata last.
:::

:::mistake
Measuring only total latency after adding streaming. Add **time to first token** to your Week 10 metrics; it's what users feel.
:::

:::cards
SSE event format? :: Lines "event:", "id:", "data:", then a blank line.
Media type? :: text/event-stream
Error mid-stream? :: An "error" event; the status is already 200.
Proxy holds the stream? :: X-Accel-Buffering: no
Metric streaming improves? :: Time to first token.
:::

:::explain Explain why streaming makes the assistant feel faster even though it isn't.
:::
""",
    "files": [
        lab("day59", "streaming.py", task=[0, 1]),
    ],
    "tasks": [
        "streaming.py: sse_event and parse_sse",
        "stream_answer and the /stream endpoint",
        "Watch it in the browser; measure time to first token with your real model",
    ],
    "done_when": "The browser shows the answer arriving word by word, then the sources.",
    "resources": [{"label": "MDN: Server-sent events", "url": "https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events"}],
    "quiz": [
        {"q": "Streaming mainly improves...", "options": ["Total latency", "Time to first token", "Accuracy", "Cost"], "answer": 1,
         "explain": "Same total, earlier first word."},
        {"q": "The model fails after 10 tokens. The client learns it via...", "options": ["HTTP 500", "An error event in the stream", "A timeout", "Nothing"], "answer": 1,
         "explain": "Headers (and status 200) were already sent."},
    ],
}

DAY60 = {
    "id": "w9d4", "folder": "day60", "notes_task": 2, "date": "2026-12-03", "weekday": "Thu",
    "title": "A usable web page", "minutes": 75,
    "why": "The agent won't open /docs. One simple, safe page is the difference between a demo and a tool.",
    "lesson": r"""
:::hook
The model answers a client's message that contained `<img src=x onerror=...>`. Your page uses `innerHTML` to display the answer. The script runs in the agent's browser. Model output is **untrusted input**, like anything a user types.
:::

## One file, no framework

A `<textarea>`, a button, a message list, and 80 lines of JavaScript. No build step, no npm, works offline in the office. You can add React later if the product grows; you probably won't need to.

## Rules for the page

- `textContent`, never `innerHTML`, for anything from the model or the user.
- `dir="auto"` on every message: the browser picks right-to-left for Arabic, left-to-right for French, per message.
- Disable the button while waiting; re-enable in `finally`.
- Show sources under the answer, readable (title > section).
- Confirm button only for `type === "confirm"`.

```python
import html
answer = 'Deux mois <script>steal()</script>'
print("as HTML it would run; as text it shows:", html.escape(answer))
```

:::analogy
A notice board where anyone can pin a message. You pin copies of the messages behind glass (textContent). Pinning the originals (innerHTML) lets someone pin a device instead of a paper.
:::

:::predict A French question gets an Arabic answer. Without dir="auto", how does it look?
---
Left-aligned Arabic with punctuation at the wrong end, numbers and Latin words jumping around. With `dir="auto"` each message picks its own direction from its first strong character.
:::

:::check
? Why re-enable the button in `finally` rather than after the fetch?
- Style
* If the request throws, code after it never runs and the form stays disabled forever
- finally is faster
- The browser requires it
> Errors are normal in a real office network.
:::

:::mistake
Loading a UI framework from a CDN. The office internet is unstable; the page breaks when the CDN doesn't load. Keep everything in the file, served by your own API.
:::

:::cards
Display model output with? :: textContent
Mixed Arabic/French messages? :: dir="auto" on each message.
Button state? :: Disabled while waiting, re-enabled in finally.
External scripts? :: None; works offline.
Serve the page? :: A GET / route returning FileResponse.
:::

:::explain Explain to a junior developer why innerHTML with model output is a security bug.
:::
""",
    "files": [
        lab("day60", "index.html", task=[0, 1]),
    ],
    "tasks": [
        "index.html: form, messages with textContent and dir=auto",
        "/chat calls with session, sources, confirm button, error handling; serve it at GET /",
        "Use it yourself for 15 minutes with real questions; list what annoys you",
    ],
    "done_when": "From the browser: ask, follow up, see sources, confirm a booking, in Arabic and French.",
    "resources": [{"label": "MDN: textContent vs innerHTML", "url": "https://developer.mozilla.org/en-US/docs/Web/API/Node/textContent"},
                  {"label": "MDN: dir attribute", "url": "https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/dir"}],
    "quiz": [
        {"q": "Model output should be inserted with...", "options": ["innerHTML", "textContent", "document.write", "eval"], "answer": 1,
         "explain": "Untrusted text never becomes HTML."},
        {"q": "What does dir=\"auto\" do?", "options": ["Translates", "Picks text direction from the content", "Auto-scrolls", "Autocompletes"], "answer": 1,
         "explain": "Right-to-left for Arabic, left-to-right for French."},
    ],
}

DAY61 = {
    "id": "w9d5", "folder": "day61", "date": "2026-12-04", "weekday": "Fri",
    "title": "Feedback loop", "minutes": 75,
    "why": "Users tell you which answers are wrong, for free, if you give them a button. Those are your most valuable test cases.",
    "lesson": r"""
:::hook
In two weeks of use, agents will see hundreds of answers. Some are wrong. Without a 👎 button you hear about one of them, by chance, at lunch. With it, you have a list, each with the question, the chunks and the answer.
:::

## What to store

| Field | Why |
|---|---|
| request_id | joins to the logs: question, chunks, prompt, answer |
| rating | +1 / -1 |
| comment | optional, short: "mauvais contrat" |
| created_at | trends per day |

The feedback row is tiny; the request id makes it rich.

## SQLite is enough

One file, no server, in Python's standard library, handles thousands of writes per second. Use `?` placeholders, always.

```python
import sqlite3
c = sqlite3.connect(":memory:")
c.execute("CREATE TABLE fb (rid TEXT PRIMARY KEY, rating INT)")
c.executemany("INSERT OR REPLACE INTO fb VALUES (?, ?)", [("r1", 1), ("r2", -1), ("r2", 1)])
print(c.execute("SELECT SUM(rating = 1), SUM(rating = -1) FROM fb").fetchone())
```

:::analogy
A restaurant comment card with the table number and time on it. "The fish was cold" alone is a complaint; with table 7 at 13:40 the chef can find the ticket and see what happened.
:::

:::predict Only 5% of answers get a rating. Is the thumbs-up rate representative?
---
No: people rate when surprised, mostly when something's wrong. Use the rate as a trend (better or worse than last week), not as accuracy. Accuracy comes from the golden set.
:::

:::check
? What makes a thumbs-down actionable?
- The timestamp alone
* The request id linking it to the question, retrieved chunks and answer
- The user's name
- A comment in capitals
> Without the trace, you know it failed but not why.
:::

:::mistake
Asking for a comment before accepting the rating. Most people just want to click. Make the comment optional, after the click.
:::

:::cards
Feedback row key? :: request_id
Same answer rated twice? :: INSERT OR REPLACE: last rating wins.
Why ? placeholders? :: Input is data, never SQL.
Thumbs-up rate is? :: A trend signal, not accuracy.
Thumbs-down export? :: Questions for error analysis and the golden set.
:::

:::explain Explain how a thumbs-down today becomes a better system next week.
:::
""",
    "files": [
        lab("day61", "feedback.py", task=[0, 1]),
    ],
    "tasks": [
        "feedback.py: init_db, record with validation and placeholders",
        "stats, by_day, export_negatives; POST /feedback and 👍/👎 buttons in the page",
        "Add the first 3 real thumbs-down questions to your golden dev set",
    ],
    "done_when": "A 👎 in the browser appears in negatives.jsonl with its question and answer.",
    "resources": [{"label": "Python: sqlite3", "url": "https://docs.python.org/3/library/sqlite3.html"}],
    "quiz": [
        {"q": "Why store the request_id with feedback?", "options": ["Uniqueness only", "To find the question, chunks and answer in the logs", "Sorting", "Privacy"], "answer": 1,
         "explain": "It turns a click into a debuggable case."},
        {"q": "The thumbs-up rate is best used as...", "options": ["Accuracy", "A trend over time", "A model score", "A target"], "answer": 1,
         "explain": "Who rates is biased; the trend still moves."},
    ],
}

DAY62 = {
    "id": "w9d6", "folder": "day62", "date": "2026-12-05", "weekday": "Sat",
    "title": "Usability test", "minutes": 180,
    "why": "You know how the system works, so you can't see where it's confusing. Watching three real users for 20 minutes each will show you.",
    "lesson": r"""
:::hook
You think booking a visit is obvious: type, read the preview, click Confirmer. The first agent you watch reads the preview, says "OK c'est fait", and closes the tab. The visit was never booked. You'd never have found that by testing yourself.
:::

## How to run it

1. 3 to 5 real users, 20 minutes each. Five users find most of the big problems.
2. 3 tasks from your scope, written as situations: "A client asks in Derja how much the deposit is."
3. **Don't help.** Say "what would you do?" and take notes. Your silence is the test.
4. Measure: success, time, errors.
5. At the end: the 10 SUS questions.

## SUS in one formula

Odd questions are positive (answer − 1), even ones negative (5 − answer), sum × 2.5 → 0 to 100. 68 is the average across thousands of products.

```python
answers = [4, 2, 4, 1, 4, 2, 5, 2, 4, 2]
score = sum((a - 1) if i % 2 == 0 else (5 - a) for i, a in enumerate(answers)) * 2.5
print(score)
```

:::analogy
A cooking show where the chef tastes everyone's dish but their own. You need someone else to taste yours.
:::

:::predict 3 of 4 users succeed at a task, but each took 3 minutes and made 2 errors. Is the task fine?
---
No. Success hides the struggle. Time and errors say the path is confusing; an agent with a client waiting won't spend 3 minutes. Report all three numbers.
:::

:::check
? A user is stuck. What do you do?
- Show them the button
* Ask "what would you do now?", wait, and note where they're stuck
- End the test
- Explain the system
> The moment they're stuck is the finding.
:::

:::mistake
Testing with friends or classmates. They're kind, technical, and guess what you meant. Test with the people from your interview.
:::

:::cards
How many users? :: 3-5 find most major problems.
Three measures per task? :: Success, time, errors.
SUS range and average? :: 0-100, average 68.
During the test you...? :: Watch and take notes, don't help.
Median time from? :: Successful attempts only.
:::

:::explain Explain why you shouldn't help a user who's stuck during a usability test.
:::
""",
    "files": [
        lab("day62", "usability_metrics.py", task=[0, 1]),
    ],
    "tasks": [
        "usability_metrics.py: SUS score and grade, task table",
        "Run the test with 3-5 real users; record tasks, times, errors and SUS",
        "Fix the worst issue the same day",
    ],
    "done_when": "A task table and a mean SUS score from real users, and one fix shipped.",
    "resources": [{"label": "SUS (usability.gov)", "url": "https://www.usability.gov/how-to-and-tools/methods/system-usability-scale.html"},
                  {"label": "Why 5 users (Nielsen)", "url": "https://www.nngroup.com/articles/why-you-only-need-to-test-with-5-users/"}],
    "quiz": [
        {"q": "SUS answers all 3 (neutral). Score?", "options": ["30", "50", "68", "75"], "answer": 1,
         "explain": "Each question contributes 2; 20 x 2.5 = 50."},
        {"q": "A user is stuck. You should...", "options": ["Help them", "Ask what they'd do and take notes", "Restart", "Skip the task"], "answer": 1,
         "explain": "Being stuck is the data."},
    ],
}

DAY63 = {
    "id": "w9d7", "folder": "day63", "retest_task": 1, "date": "2026-12-06", "weekday": "Sun",
    "title": "Usability report", "minutes": 150,
    "why": "Phase 2's demo is next week's evaluation plus this: proof that real people can use it.",
    "lesson": r"""
:::hook
"Users liked it" is what everyone writes. "4 agents, 3 tasks, booking succeeded 3/4 with a median of 88 s, SUS 72 (C); the confirm button was missed by 2/4, fixed by moving it above the details" is what an interviewer remembers.
:::

## Severity × frequency

| | 1 user | most users |
|---|---|---|
| **high** (wrong action, data loss, gives up) | fix this week | fix today |
| **medium** (slow, confusing) | backlog | fix this week |
| **low** (cosmetic) | maybe never | backlog |

```python
issues = [("confirm button missed", "high", 2), ("doc ids unreadable", "high", 3), ("Enter sends", "low", 1)]
rank = {"high": 0, "medium": 1, "low": 2}
for name, sev, n in sorted(issues, key=lambda i: (rank[i[1]], -i[2])):
    print(f"[{sev}] {name} ({n}/4)")
```

:::analogy
An emergency room triage: the bleeding patient goes first, even if ten people with colds arrived earlier.
:::

## Close the loop

Each issue → a change → (next round) a check that it's fixed. And each usability finding about **answers** (not the UI) becomes a Week 10 measurement: "the pet clause failed on scanned contracts" → measure citation accuracy per document type.

:::predict A high-severity issue you can't fix before Week 10. What goes in the report?
---
The issue, its severity and frequency, and why it's not fixed yet (with the plan). Hiding it means someone finds it during your demo.
:::

:::check
? Which issue gets fixed first?
- [low] seen by 4/4 users
* [high] seen by 2/4 users
- [medium] seen by 1/4 users
- The easiest one
> Severity first, then frequency.
:::

:::mistake
Reporting only the SUS score. A 72 tells you "okay"; it doesn't tell you what to change. The issues list is the useful part.
:::

:::cards
Issue tag? :: [high], [medium] or [low], plus how many users.
Fix order? :: Severity, then frequency.
Answer-quality findings go to? :: Week 10 measurements.
Unfixed high issue? :: Report it with the plan.
Report includes? :: Participants, tasks, table, SUS, issues, changes, next.
:::

:::explain Summarize your usability test in three sentences with two numbers.
:::
""",
    "files": [
        lab("day63", "usability.md", task=0),
    ],
    "tasks": [
        "usability.md: results, ranked issues, changes made",
        "Beat the Week 9 boss (8/10)",
        "Retro in notes; push Week 9 with a screenshot of the page",
    ],
    "done_when": "Report committed, a high-severity issue fixed, and 8/10 on the boss.",
    "resources": [],
    "quiz": [
        {"q": "Fix first?", "options": ["[low] 4/4 users", "[high] 2/4 users", "[medium] 1/4 users", "The shortest fix"], "answer": 1,
         "explain": "Severity before frequency."},
    ],
    "retest": [
        {"q": "Who confirms an action?", "options": ["The model", "A human click in the UI", "The API", "Nobody"], "answer": 1,
         "explain": "The model never presses the button."},
        {"q": "Same booking confirmed twice. Result?", "options": ["Two visits", "One visit; the second click returns already_done", "An error", "Random"], "answer": 1,
         "explain": "Idempotent action id."},
        {"q": "A pending action is confirmed 1 hour later. With a 10-minute TTL...", "options": ["It runs", "It's expired", "It runs twice", "It's cancelled silently"], "answer": 1,
         "explain": "Old previews shouldn't execute."},
        {"q": "Why rewrite 'et avec un chat ?' before retrieval?", "options": ["Grammar", "The retriever has no memory of the previous question", "Translation", "Cost"], "answer": 1,
         "explain": "Join it to the last user question."},
        {"q": "An action request without a date. The chat should...", "options": ["Guess tomorrow", "Ask for the missing details", "Refuse", "Book any slot"], "answer": 1,
         "explain": "Ask, don't guess."},
        {"q": "SSE media type?", "options": ["application/json", "text/event-stream", "text/html", "multipart/mixed"], "answer": 1,
         "explain": "Server-Sent Events."},
        {"q": "Streaming improves mostly...", "options": ["Accuracy", "Time to first token", "Cost", "Total latency"], "answer": 1,
         "explain": "The first word arrives early."},
        {"q": "Model output in the page goes through...", "options": ["innerHTML", "textContent", "eval", "document.write"], "answer": 1,
         "explain": "Untrusted text, never HTML."},
        {"q": "The feedback row's most useful field is...", "options": ["created_at", "request_id", "rating", "comment"], "answer": 1,
         "explain": "It links to the full trace."},
        {"q": "SUS average across products?", "options": ["50", "68", "80", "100"], "answer": 1,
         "explain": "Above 68 is above average."},
    ],
}

WEEK9 = {
    "n": 9, "phase": "Phase 2", "title": "Build II", "dates": "Nov 30-Dec 6",
    "goal": "Tool calling and a usable UI.",
    "gate": "Usable demo",
    "days": [DAY57, DAY58, DAY59, DAY60, DAY61, DAY62, DAY63],
}
