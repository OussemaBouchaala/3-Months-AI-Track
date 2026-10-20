"""Week 12: Present (Dec 21-27, 2026)."""
from lab_files import lab

DAY78 = {
    "id": "w12d1", "folder": "day78", "date": "2026-12-21", "weekday": "Mon",
    "title": "The demo script", "minutes": 75,
    "why": "Most people who see your project will see 4 minutes of video. The script decides what they remember.",
    "lesson": r"""
:::hook
Two demos of the same project. The first opens with "Hi, my name is Oussema and today I'm going to present my project, which is a RAG system using..." and shows the architecture for 90 seconds. The second opens with "Rental agents answer 40 identical questions a day", then pastes a Derja question and the answer appears with its source. People stop watching the first one at 0:15.
:::

## The shape of a 4-minute demo

| scene | time | what |
|---|---|---|
| Hook | 0:20 | the problem with a number |
| Live use | 2:00 | real questions: Arabic/Derja, follow-up, action with confirmation |
| Honest failure | 0:25 | an "I don't know", or a known weakness |
| Numbers | 0:40 | the results table |
| How it runs | 0:25 | docker compose up, privacy |
| Close | 0:20 | next step, your name, the link |

```python
scenes = [20, 45, 30, 40, 25, 40, 25, 20]
total = sum(scenes)
print(f"{total // 60}:{total % 60:02d}", "fits" if 180 <= total <= 300 else "rewrite")
```

:::analogy
A movie trailer: it opens on action, not on the studio's history, shows the best scenes, and ends with the title and the date. Your name and the repo link are the title card.
:::

## Show, don't tell

"It supports Arabic" is telling. Pasting "شنوة الضمان كي نكري دار؟" and watching the answer arrive is showing. Every claim in the script should be something visible on screen.

:::predict Should the demo include something that fails?
---
Yes, deliberately: an "I don't know" on an out-of-scope question shows the system is honest, which is the property clients care about most. A demo where everything works looks rehearsed (because it is).
:::

:::check
? What goes in the first 20 seconds?
- Your name and education
- The architecture diagram
* The user's problem, with a number
- The tech stack
> Earn the next 4 minutes first.
:::

:::mistake
Typing questions live, slowly, with typos. Prepare them in a text file and paste. Same for waiting on the model: cut the wait in editing.
:::

:::cards
Demo length? :: 3 to 5 minutes.
First scene? :: The problem with a number, under 30 seconds.
Live scenes show? :: Real questions: Arabic/Derja, follow-up, confirmed action.
Include a failure? :: Yes: an honest "I don't know".
Last scene? :: Next step, your name, the link.
:::

:::explain Pitch your demo's hook out loud in 20 seconds.
:::
""",
    "files": [
        lab("day78", "demo_script.md", task=[0, 1]),
    ],
    "tasks": [
        "demo_script.md: hook, live scenes, the honest failure",
        "Numbers, deployment and closing scenes; total 3-5 minutes",
        "Prepare the exact questions in a text file for pasting",
    ],
    "done_when": "A script of 3-5 minutes that you can read aloud on time.",
    "resources": [],
    "quiz": [
        {"q": "Best opening for the demo?", "options": ["'Hi, my name is...'", "The architecture", "The problem with a number", "The tech stack"], "answer": 2,
         "explain": "Why it matters first."},
        {"q": "Why show an 'I don't know' answer?", "options": ["Filler", "It shows the system doesn't invent answers", "To lower expectations", "It's required"], "answer": 1,
         "explain": "Honesty is a feature."},
    ],
}

DAY79 = {
    "id": "w12d2", "folder": "day79", "notes_task": 2, "date": "2026-12-22", "weekday": "Tue",
    "title": "Rehearse and time it", "minutes": 75,
    "why": "A demo that runs 7 minutes loses most of its audience. Timing is the difference between a script and a demo.",
    "lesson": r"""
:::hook
Your script reads in 3:45 in your head. The first rehearsal takes 5:50: you speak slower on camera, the model takes 5 seconds to answer twice, and you explain the follow-up scene twice because it didn't feel clear.
:::

## Estimate, then measure

Words ÷ 130 words per minute = speaking time at a calm demo pace. Add the seconds the screen needs (the app answering). If the estimate already exceeds the plan, cut words now.

```python
scene = "A client writes in Derja asking about the deposit. I paste it as is. The answer comes back in Derja in four seconds, with its source."
words = len(scene.split())
print(words, "words ->", round(words / 130 * 60), "s spoken + 4 s waiting")
```

:::analogy
A radio host with a 3-minute slot: they time the script and know which paragraph to drop if the guest runs long. Nothing gets cut live by accident.
:::

## Rehearse with laps

Use a stopwatch's lap button at each scene change. Compare with the plan scene by scene: the total tells you you're long, the laps tell you **where**.

## Cut, don't rush

Running long? Remove a sentence or a whole scene. Speaking faster makes you harder to follow and adds filler words.

:::predict Your rehearsal is 40 s over, all in the "numbers" scene. Fix?
---
Show the table and say one sentence about the key number and one about the trade-off. Viewers can pause to read the rest; you don't need to read every cell.
:::

:::check
? Over time by 45 seconds. Best move?
- Speak faster
* Cut the least important sentences or a whole scene
- Speed up the video 1.25x
- Remove the hook
> Rushed speech loses people; shorter scripts don't.
:::

:::mistake
Rehearsing only in your head. Out loud, with the app running and a stopwatch, at least twice. The first real rehearsal always surprises you.
:::

:::cards
Calm demo pace? :: About 130 words per minute.
Speaking time estimate? :: words / wpm × 60 + waiting time.
Laps tell you? :: Which scene runs long.
Running long? :: Cut, don't rush.
How many rehearsals? :: At least two, out loud, with a stopwatch.
:::

:::explain Explain why you cut scenes instead of speaking faster.
:::
""",
    "files": [
        lab("day79", "timing.py", task=[0, 1]),
    ],
    "tasks": [
        "timing.py: parse the script, estimate speaking time, flag long scenes",
        "Rehearse twice with laps; compare and cut",
        "Note in your notes which sentences you cut and why",
    ],
    "done_when": "The second rehearsal is within 15 seconds of the plan.",
    "resources": [],
    "quiz": [
        {"q": "140 words at 130 wpm, plus 5 s of waiting. Scene time?", "options": ["About 50 s", "About 70 s", "About 1:40", "About 30 s"], "answer": 1,
         "explain": "140/130 × 60 ≈ 65 s + 5 s."},
        {"q": "What do rehearsal laps tell you that the total doesn't?", "options": ["Nothing", "Which scene runs long", "The wpm", "Filler words"], "answer": 1,
         "explain": "Fix the right scene."},
    ],
}

DAY80 = {
    "id": "w12d3", "folder": "day80", "date": "2026-12-23", "weekday": "Wed",
    "title": "CV bullets", "minutes": 75,
    "why": "Recruiters read a CV in seconds. Three months of work need to fit in lines that say what, with what, and how well.",
    "lesson": r"""
:::hook
"Worked on an AI chatbot project using Python and various NLP technologies." Every junior CV has this line. It says nothing a recruiter can believe or compare. You have numbers most candidates don't: accuracy with intervals, latency, cost, real users.
:::

## The formula

**Verb** + **what** + **with what** + **result with a number**.

```python
parts = {"verb": "Built", "what": "a bilingual RAG assistant for a real estate agency",
         "with": "(FastAPI, pgvector, Ollama)", "result": "answering 86% of 42 held-out questions correctly at 0.004 USD each"}
print(" ".join(parts.values()) + ".")
```

:::analogy
A product label at the supermarket: name, key ingredient, weight, price. Shoppers compare in two seconds because every label has the same fields.
:::

## What to cut

- Weak openers: "Responsible for", "Worked on", "Helped", "Participated in".
- Adjectives about yourself: "passionate", "hard-working".
- Vague quantities: "various", "several", "many".

## What to keep

One bullet per strong result: the system and its accuracy; the evaluation method; the Arabic retrieval gain; the deployment; the usability or cost result. Four to six bullets for the whole program, under one "Projects" entry with the link.

:::predict "Improved retrieval." What's missing?
---
How much, on what, and how: "Improved Arabic retrieval recall@5 from 0.61 to 0.79 on 100 ARCD questions with normalization, light stemming and hybrid BM25 search."
:::

:::check
? Which bullet is strongest?
- "Passionate about AI and machine learning."
- "Worked on various NLP tasks."
* "Deployed a RAG assistant with Docker Compose and CI, used by 4 agents, at 25 TND a month."
- "Responsible for the backend."
> Verb, what, tool, numbers.
:::

:::mistake
Numbers you can't defend. In the interview, every number on the CV can become "how did you measure that?". Use only the ones from your reports.
:::

:::cards
Bullet formula? :: Verb + what + with what + result with a number.
Weak openers? :: Responsible for, worked on, helped, participated in.
Length? :: 10-30 words, one line or two.
How many bullets? :: 4-6 for the program.
Every number? :: Must come from your reports, defensible in an interview.
:::

:::explain Read your best bullet aloud and explain where each number comes from.
:::
""",
    "files": [
        lab("day80", "cv_bullets.py", task=[0, 1]),
    ],
    "tasks": [
        "cv_bullets.py: the linter, score and review",
        "4-6 bullets from your real numbers, each scoring 100",
        "Update your CV with a Projects entry and the repository link",
    ],
    "done_when": "Your CV has the new bullets, each passing the linter.",
    "resources": [],
    "quiz": [
        {"q": "Which opener is strongest?", "options": ["Responsible for", "Helped with", "Built", "Worked on"], "answer": 2,
         "explain": "A concrete action verb."},
        {"q": "A CV number should be...", "options": ["Impressive", "Measured and defensible in an interview", "Rounded up", "Optional"], "answer": 1,
         "explain": "Every number is a future interview question."},
    ],
}

DAY81 = {
    "id": "w12d4", "folder": "day81", "notes_task": 2, "date": "2026-12-24", "weekday": "Thu",
    "title": "The LinkedIn post", "minutes": 75,
    "why": "The video and the repo only help if people see them. One good post puts them in front of recruiters and engineers in Tunisia and beyond.",
    "lesson": r"""
:::hook
LinkedIn shows about two lines before "...see more". "I'm thrilled to announce that I completed my project!" gets scrolled past. "Rental agents in Sousse answer 40 identical questions a day. I spent 6 weeks building them an assistant." gets the click.
:::

## Structure

1. **Hook**: a number or a surprising fact, under 150 characters.
2. **What and for whom**, in plain words (no "leveraging cutting-edge LLMs").
3. **Three numbers**: accuracy, latency, cost, or users.
4. **One lesson or failure**: the part people comment on.
5. **Link** and 1-5 hashtags.

```python
post = "Rental agents answer 40 identical questions a day. I built them an assistant.\n\n..."
first = post.splitlines()[0]
print(len(first), "chars in the hook:", first)
```

:::analogy
A newspaper headline and first paragraph: the headline makes you read, the first paragraph tells you the story, the rest is for those who want details.
:::

## Plain text

LinkedIn doesn't render Markdown: `**bold**` shows the asterisks. Use short paragraphs and blank lines instead.

:::predict Post with the video uploaded natively, or a YouTube link?
---
Native video usually gets more reach on LinkedIn, but a link keeps one place for views and comments. A common compromise: native video in the post, repo link in the text.
:::

:::check
? Which detail makes people comment?
- The tech stack list
* An honest failure or surprise ("the biggest gain wasn't the model, it was Arabic spelling")
- Ten hashtags
- "Thanks for reading!"
> Lessons start conversations; stack lists don't.
:::

:::mistake
Publishing and disappearing. Reply to comments in the first hour; it's when the post is shown to the most people, and it's where conversations with recruiters start.
:::

:::cards
Hook length? :: Under 150 characters, with a number or surprise.
Numbers in the post? :: At least three, from your reports.
Markdown? :: Not rendered; use plain text and blank lines.
Hashtags? :: 1 to 5.
After posting? :: Reply to comments in the first hour.
:::

:::explain Explain your project in the first two lines of a post, out loud.
:::
""",
    "files": [
        lab("day81", "linkedin_post.md", task=[0, 1]),
    ],
    "tasks": [
        "linkedin_post.md: hook, what and for whom, three numbers",
        "One lesson, the link, hashtags; under 1,800 characters",
        "Ask one person to read it and tell you the one thing they remember",
    ],
    "done_when": "The post passes the check and is ready to publish with the video.",
    "resources": [],
    "quiz": [
        {"q": "Best hook?", "options": ["'I'm excited to announce...'", "'Agents answer 40 identical questions a day. I built them an assistant.'", "'Hello network!'", "'#AI #ML #RAG'"], "answer": 1,
         "explain": "A number and a story in two lines."},
        {"q": "**Bold** in a LinkedIn post shows as...", "options": ["Bold", "The asterisks", "Italic", "Nothing"], "answer": 1,
         "explain": "No Markdown rendering."},
    ],
}

DAY82 = {
    "id": "w12d5", "folder": "day82", "date": "2026-12-25", "weekday": "Fri",
    "title": "Interview answers", "minutes": 75,
    "why": "The project gets you the interview. These five answers, spoken clearly with numbers, get you the offer.",
    "lesson": r"""
:::hook
"Tell me about a project you're proud of." You know everything about it, so you start at the beginning: the course, the weeks, the first Python file... Four minutes later the interviewer hasn't heard a single result. Knowing the material isn't the same as having the answer ready.
:::

## Five questions you'll get

1. A project you're proud of.
2. The hardest technical problem.
3. How you knew it worked (evaluation).
4. Something that failed, and what you learned.
5. Why this design over the alternatives.

## STAR, mostly Action

**S**ituation (one sentence) → **T**ask (one sentence) → **A**ction (most of the answer: what *I* did and why) → **R**esult (numbers).

```python
answer = {"S": 1, "T": 1, "A": 4, "R": 1}   # sentences
total = sum(answer.values())
print({k: f"{v / total:.0%}" for k, v in answer.items()})
```

:::analogy
A doctor's case presentation to colleagues: patient and symptoms in one line, then the reasoning and the decisions in detail, then the outcome. Nobody wants the patient's whole life story.
:::

## Length

30-90 seconds spoken (80-250 words). Long enough to show reasoning, short enough that the interviewer can follow up. Follow-ups are good: they mean you said something interesting.

:::predict The interviewer asks "how did you evaluate it?" and you say "I tested it and it worked well". What follows?
---
A harder question, or a lower score. Say: golden set from real questions, dev/test split, the judge's agreement with your labels, the score with its interval, and the failure analysis. You have all of it; say it.
:::

:::check
? In the failure answer, what matters most?
- That the failure was someone else's fault
- That it was small
* What you changed afterwards and what you learned
- The exact date
> Interviewers listen for learning, not perfection.
:::

:::mistake
"We did..." all the time. The interviewer is hiring you. Say "I" for what you did, and "we" only for genuinely shared work.
:::

:::cards
STAR? :: Situation, Task, Action, Result.
Most of the answer? :: Action: what I did and why.
Length? :: 30-90 seconds, 80-250 words.
Failure answer must include? :: What you learned and changed.
Design answer must include? :: The alternative and the trade-off.
:::

:::explain Answer Q3 (evaluation) out loud without notes, in under 90 seconds.
:::
""",
    "files": [
        lab("day82", "interview_answers.md", task=[0, 1]),
    ],
    "tasks": [
        "interview_answers.md: Q1-Q3 with your real numbers",
        "Q4 (failure) and Q5 (design trade-off); three questions for them",
        "Record yourself answering Q1 and Q3; listen once",
    ],
    "done_when": "You can answer Q1 and Q3 out loud, without notes, in 30-90 seconds each.",
    "resources": [],
    "quiz": [
        {"q": "Which STAR part should be longest?", "options": ["Situation", "Task", "Action", "Result"], "answer": 2,
         "explain": "What you did and why."},
        {"q": "A good spoken answer lasts...", "options": ["10 seconds", "30-90 seconds", "5 minutes", "As long as needed"], "answer": 1,
         "explain": "Room for follow-ups."},
    ],
}

DAY83 = {
    "id": "w12d6", "folder": "day83", "date": "2026-12-26", "weekday": "Sat",
    "title": "Record the demo", "minutes": 180,
    "why": "Today the demo becomes a video that works for you while you sleep: on the README, the post, and the message to Anis.",
    "lesson": r"""
:::hook
You record in one take, upload, and post. Later you watch it: 6:10 long, 14 "euh", and 8 seconds of silence while the model answered. A reviewer would have caught all three in a minute. Today the reviewer is a script.
:::

## Recording setup

- **OBS Studio** (free): screen at 1080p, microphone, no webcam needed.
- A quiet room; the phone's earphones mic beats the laptop's mic.
- Browser zoomed to 125-150%, notifications off, a clean browser profile.
- The questions in a text file, ready to paste.
- Record scene by scene; it's easier to redo one scene than the whole thing.

## Check it with numbers

Upload as **unlisted** to YouTube, download the auto-captions (.srt), or run Whisper locally. Then measure:

```python
subs = [(0.0, 4.0, "Rental agents answer forty questions a day."), (4.5, 8.0, "Euh, so I built an assistant."),
        (16.0, 19.0, "It answers in Derja.")]
words = sum(len(t.split()) for _, _, t in subs)
spoken = sum(e - s for s, e, _ in subs)
print(round(words / spoken * 60), "wpm |", [round(b[0] - a[1], 1) for a, b in zip(subs, subs[1:]) if b[0] - a[1] >= 3], "s of dead air")
```

:::analogy
A singer listening to the studio take before releasing it. The take that felt great live has a flat note at 2:14 that only the recording reveals.
:::

## Fix in editing

Dead air while the model thinks: cut it (or speed that part 2x, and say so). Fillers: re-record the scene. Too long: drop a scene, not words in a hurry.

:::predict The video is 4:30 but has 9 pauses over 3 seconds. Publish?
---
Cut the pauses first: they make the app look slow and the video feel longer than it is. In a free editor (Shotcut, DaVinci Resolve, or YouTube's own trimmer) that's 15 minutes of work.
:::

:::check
? Why upload unlisted first?
- It's faster
* To get auto-captions and check the video before anyone sees it
- YouTube requires it
- For better quality
> Review privately, then publish.
:::

:::mistake
Showing real client data in the video. Use the masked versions, fake names, and listings you're allowed to show. A demo is public forever.
:::

:::cards
Recording tool? :: OBS Studio, 1080p.
Subtitles from? :: YouTube auto-captions or Whisper, as .srt.
Good pace? :: 110-170 words per minute.
Dead air? :: Cut pauses over 3 seconds.
Real client data in the video? :: Never; use masked or fake data.
:::

:::explain Explain what you'll fix if the check says "too many fillers".
:::
""",
    "files": [
        lab("day83", "demo_qc.py", task=[0, 1]),
    ],
    "tasks": [
        "demo_qc.py: parse SRT, pace, fillers, pauses, verdict",
        "Record the demo, check it, fix it until 'Ready to publish'",
        "Publish the video; add it to the README",
    ],
    "done_when": "The video is published, 3-5 minutes, and passes the check.",
    "resources": [{"label": "OBS Studio", "url": "https://obsproject.com/"},
                  {"label": "Whisper (local transcription)", "url": "https://github.com/openai/whisper"}],
    "quiz": [
        {"q": "8 seconds of silence while the model answers. Best fix?", "options": ["Keep it", "Cut it or speed it up in editing", "Talk faster elsewhere", "Remove the scene"], "answer": 1,
         "explain": "Dead air feels much longer on video."},
        {"q": "A good demo pace is roughly...", "options": ["60-90 wpm", "110-170 wpm", "200-250 wpm", "Any"], "answer": 1,
         "explain": "Calm but not sleepy."},
    ],
}

DAY84 = {
    "id": "w12d7", "folder": "day84", "retest_task": 1, "date": "2026-12-27", "weekday": "Sun",
    "title": "The message to Anis", "minutes": 150,
    "why": "Twelve weeks ago Anis asked for accuracy, cost and latency. Today you answer, with a working system behind every number.",
    "lesson": r"""
:::hook
Anis gets dozens of messages a week. Most say "I'm very motivated, here is my CV". Yours says: "You asked for accuracy, latency and cost. 86% on 42 held-out questions, 7.4 s p95, 25 TND a month. Here's the code and a 4-minute video." That's the message he forwards to his team.
:::

## The shape

1. **Subject**: specific ("Accuracy, latency and cost of the agency assistant").
2. **Context**: one sentence: when you spoke, what he asked.
3. **The three numbers**, with what they're measured on.
4. **One limitation**: it shows judgment.
5. **Two links**: repository, video.
6. **One small ask**: 20 minutes of feedback, ending with a question mark.

```python
msg_words = 190
print("reading time:", round(msg_words / 230 * 60), "seconds")
```

Under a minute to read. Everything else is behind the links.

:::analogy
An executive summary: the decision-maker reads one page, and the 40-page report is there if they want it. Your repository is the report; the message is the summary.
:::

## The ask

Small and specific is easy to say yes to: "20 minutes in early January for feedback on the evaluation" beats "any opportunity in your company". If he says yes, you're in a conversation; that's the goal.

:::predict He doesn't reply in a week. What now?
---
One short follow-up after 7-10 days, adding something new (the LinkedIn post's reception, a fix you made). Then move on and send the same kind of message to other people; the project and the video work for any of them.
:::

:::check
? Which ask is best?
- "Let me know if you have any opportunities."
* "Would you have 20 minutes in early January to give me feedback on the evaluation?"
- "Please review my whole repository."
- No ask
> Small, specific, easy to accept.
:::

:::mistake
A long message retelling the 12 weeks. He asked three questions; answer them first. The story is in the README and the video for whoever wants it.
:::

:::cards
Subject line? :: Specific, under 80 characters.
First paragraph? :: Context: when you spoke, what he asked.
The numbers? :: Accuracy with test size, p95 latency, monthly cost.
Ask? :: Small, specific, ends with a question mark.
No reply after a week? :: One short follow-up with something new.
:::

:::explain Read your message aloud and check it answers his three questions in the first half.
:::
""",
    "files": [
        lab("day84", "message_to_anis.md", task=0),
    ],
    "tasks": [
        "message_to_anis.md: written, checked, and sent",
        "Beat the Week 12 boss (8/10)",
        "Final retro in notes: what the 12 weeks taught you, what's next. Push everything.",
    ],
    "done_when": "The message is sent, and you scored 8/10 on the final boss.",
    "resources": [],
    "quiz": [
        {"q": "What leads the message?", "options": ["Your motivation", "The three numbers he asked for", "Your CV", "The architecture"], "answer": 1,
         "explain": "Answer his question first."},
    ],
    "retest": [
        {"q": "The demo's first 20 seconds should show...", "options": ["Your name and school", "The user's problem with a number", "The tech stack", "The architecture"], "answer": 1,
         "explain": "Earn attention first."},
        {"q": "Why include an 'I don't know' scene?", "options": ["Filler", "It proves the system doesn't invent", "To shorten the demo", "Required"], "answer": 1,
         "explain": "Honesty is what clients need."},
        {"q": "Rehearsal runs 45 s long. Fix?", "options": ["Speak faster", "Cut sentences or a scene", "Speed up the video", "Ignore it"], "answer": 1,
         "explain": "Cut, don't rush."},
        {"q": "Strongest CV bullet opener?", "options": ["Responsible for", "Worked on", "Built", "Helped"], "answer": 2,
         "explain": "A concrete action verb."},
        {"q": "Every number on the CV must be...", "options": ["Rounded up", "Measured and defensible", "Above 90%", "In percent"], "answer": 1,
         "explain": "It will be asked about."},
        {"q": "LinkedIn post hook should be...", "options": ["'Excited to announce'", "Under 150 characters with a number or surprise", "A list of hashtags", "A link"], "answer": 1,
         "explain": "It earns the 'see more' click."},
        {"q": "In STAR, the longest part is...", "options": ["Situation", "Task", "Action", "Result"], "answer": 2,
         "explain": "What you did and why."},
        {"q": "A spoken interview answer should last...", "options": ["10 s", "30-90 s", "3-5 min", "Unlimited"], "answer": 1,
         "explain": "Leave room for follow-ups."},
        {"q": "8 s of dead air in the demo video. Fix?", "options": ["Leave it", "Cut it in editing", "Add music", "Re-record everything"], "answer": 1,
         "explain": "Trim the wait."},
        {"q": "Best ask to Anis?", "options": ["Any opportunity?", "20 minutes of feedback on the evaluation in early January?", "Review my repo", "Nothing"], "answer": 1,
         "explain": "Small, specific, easy to accept."},
    ],
}

WEEK12 = {
    "n": 12, "phase": "Phase 2", "title": "Present", "dates": "Dec 21-27",
    "goal": "Demo video and the message to Anis.",
    "gate": "Message sent",
    "days": [DAY78, DAY79, DAY80, DAY81, DAY82, DAY83, DAY84],
}
