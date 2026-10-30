"""A CV line is read in 6 seconds.

"Worked on an AI chatbot" says nothing. "Built a bilingual RAG assistant answering 86% of
42 held-out questions correctly at 0.004 USD each" says **what**, **how well**, and **at
what cost**. This linter checks your bullets for exactly that.

1. `STRONG_VERBS`, `WEAK_PHRASES`, `TOOLS`: the word lists the rules use.
2. `BULLETS`: your CV bullets for this project.
3. `lint`: everything wrong with one bullet.
4. `score`: 100 minus 20 per problem.
5. `review`: all bullets, worst first, with their problems.
"""
import re

STRONG_VERBS = {"built", "designed", "deployed", "evaluated", "reduced", "improved", "shipped", "led", "automated",
                "implemented", "created", "measured", "cut", "migrated", "trained", "wrote", "launched", "integrated"}
WEAK_PHRASES = ["responsible for", "worked on", "helped", "participated in", "involved in", "various", "passionate",
                "hard-working", "team player", "state-of-the-art", "cutting-edge"]
TOOLS = {"python", "fastapi", "docker", "postgres", "pgvector", "pytorch", "scikit-learn", "rag", "llm", "ollama",
         "github actions", "ci", "sql", "pandas", "tesseract", "ocr", "mcp", "anthropic", "openai",
         "bm25", "embeddings", "nlp", "fine-tuning", "bootstrap"}

BULLETS = [   # replace with your real numbers from results.md
    "Built a bilingual RAG assistant (FastAPI, pgvector, Ollama) answering agency questions with 86% accuracy on 42 held-out questions.",
    "Designed an evaluation harness with bootstrap confidence intervals and an LLM judge at 0.81 kappa agreement with human labels.",
    "Reduced retrieval misses on Arabic questions by 11 points with normalization, light stemming and hybrid BM25 search.",
    "Deployed the system with Docker Compose and GitHub Actions CI, running on the client's office PC for 25 TND a month.",
    "Implemented an OCR pipeline with Tesseract for 80 scanned contracts, flagging pages below 0.9 text quality for review.",
]


def lint(bullet):
    """Every problem of one bullet (`[]` = good). The rules recruiters apply:

    - Start with a strong past-tense verb (built, reduced...): you did it.
    - Contain a number: a result, a size, a cost.
    - 10 to 30 words: one idea, readable in one breath.
    - No weak phrases ("worked on", "various", "passionate").
    - Name a tool or technique. `\\b...\\b` matches whole words only, so
      "specialized" doesn't count as "ci".

    Example:
        >>> lint("Worked on an AI chatbot for a company using various technologies.")
        ['start with a strong past-tense verb', 'add a number (%, users, seconds, TND...)', 'weak phrase: worked on', 'weak phrase: various', 'name a tool or technique']
        >>> lint("Built a bilingual RAG assistant with FastAPI and pgvector, answering 86% of 42 held-out client questions correctly.")
        []
    """
    problems = []
    words = bullet.split()
    first = re.sub(r"[^\w-]", "", words[0].lower()) if words else ""
    if first not in STRONG_VERBS:
        problems.append("start with a strong past-tense verb")
    if not re.search(r"\d", bullet):
        problems.append("add a number (%, users, seconds, TND...)")
    if len(words) > 30:
        problems.append(f"too long ({len(words)} words, max 30)")
    if len(words) < 10:
        problems.append("too short")
    low = bullet.lower()
    problems += [f"weak phrase: {p}" for p in WEAK_PHRASES if p in low]
    if not any(re.search(rf"\b{re.escape(t)}\b", low) for t in TOOLS):
        problems.append("name a tool or technique")
    return problems


def score(bullet):
    """100 minus 20 per problem, never below 0.

    Example:
        >>> score("Built RAG in 3 days."), score("Worked on various things, responsible for helping.")
        (80, 0)
    """
    return max(0, 100 - 20 * len(lint(bullet)))


def review(bullets):
    """All bullets, worst first, each with its problems, then the average.
    Fix from the top.

    Example:
        >>> print("\\n".join(review(["Built RAG in 3 days.", "Built a RAG assistant with FastAPI answering 86% of 42 held-out questions."])))
         80  Built RAG in 3 days.
              - too short
        100  Built a RAG assistant with FastAPI answering 86% of 42 held-out questions.
        average 90
    """
    lines = []
    for b in sorted(bullets, key=score):
        lines.append(f"{score(b):3}  {b}")
        lines += [f"      - {p}" for p in lint(b)]
    lines.append(f"average {round(sum(map(score, bullets)) / len(bullets)) if bullets else 0}")
    return lines


if __name__ == "__main__":
    before = ["Worked on an AI chatbot for a company using various technologies.",
              "Responsible for the evaluation of the model."]
    print("--- typical first drafts")
    print("\n".join(review(before)))
    print("\n--- BULLETS")
    print("\n".join(review(BULLETS)))
