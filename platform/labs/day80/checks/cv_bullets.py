li, sc, rv = fn("lint"), fn("score"), fn("review")
bad = "Worked on an AI chatbot for a company using various technologies."
good = "Built a bilingual RAG assistant with FastAPI and pgvector, answering 86% of 42 held-out client questions correctly."
check("a strong bullet has no problems", lambda: li(good) == [])
check("a weak bullet: verb, number, weak phrases", lambda: set(li(bad)) >= {"start with a strong past-tense verb", "add a number (%, users, seconds, TND...)", "weak phrase: worked on", "weak phrase: various"})
check("weak bullet without a tool word is flagged", lambda: "name a tool or technique" in li(bad))
check("too short and too long", lambda: "too short" in li("Built RAG in 3 days.") and any(p.startswith("too long (31 words") for p in li("Built " + "x " * 27 + "with Docker 9")))
check("tool words match whole words only", lambda: "name a tool or technique" in li("Built a specialized scraper collecting 4000 apartment listings every single night quickly."))
check("score: 100 - 20 per problem, min 0", lambda: sc(good) == 100 and sc(bad) == max(0, 100 - 20 * len(li(bad))) and sc("Worked on various things, responsible for helping.") == 0)
check("review: worst first, problems indented, average", lambda: (lambda r: r[0].startswith(f"{sc(bad):3}  Worked") and r[1].startswith("      - ") and r[-1] == f"average {round((sc(bad) + 100) / 2)}")(rv([good, bad])))
B = lambda: var("BULLETS")
check("your BULLETS: 4 to 6 bullets", lambda: 4 <= len(B()) <= 6)
check("every bullet in BULLETS scores 100", lambda: B() and all(sc(b) == 100 for b in B()) or (_ for _ in ()).throw(CheckFailed("; ".join(f"{b[:40]}...: {li(b)}" for b in B() if li(b)) or "add bullets")))
