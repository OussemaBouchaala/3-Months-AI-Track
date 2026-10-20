# A CV line is read in 6 seconds. "Worked on an AI chatbot" says nothing. "Built a bilingual RAG assistant
# answering 86% of 42 held-out questions correctly at 0.004 USD each" says what, how well, and at what cost.
import re

STRONG_VERBS = {"built", "designed", "deployed", "evaluated", "reduced", "improved", "shipped", "led", "automated",
                "implemented", "created", "measured", "cut", "migrated", "trained", "wrote", "launched", "integrated"}
WEAK_PHRASES = ["responsible for", "worked on", "helped", "participated in", "involved in", "various", "passionate",
                "hard-working", "team player", "state-of-the-art", "cutting-edge"]
TOOLS = {"python", "fastapi", "docker", "postgres", "pgvector", "pytorch", "scikit-learn", "rag", "llm", "ollama",
         "github actions", "ci", "sql", "pandas", "tesseract", "ocr", "mcp", "anthropic", "openai",
         "bm25", "embeddings", "nlp", "fine-tuning", "bootstrap"}

BULLETS = [
    # TODO: 4 to 6 bullets about your Phase 2 project (and Phase 1 if you like), in English.
]


def lint(bullet):
    """List of problems ([] = good):
    "start with a strong past-tense verb" if the first word (lowercased, stripped of punctuation) is not in STRONG_VERBS;
    "add a number (%, users, seconds, TND...)" if there is no digit;
    "too long (N words, max 30)" if more than 30 words;
    "too short" if fewer than 10 words;
    "weak phrase: <phrase>" for each WEAK_PHRASES found (case-insensitive);
    "name a tool or technique" if no TOOLS word appears (case-insensitive, whole words)."""
    # TODO
    ...


def score(bullet):
    """100 minus 20 per problem, never below 0."""
    # TODO
    ...


def review(bullets):
    """Lines "<score>  <bullet>" sorted by score ascending (worst first), then each problem indented "      - ...".
    A last line "average <mean score rounded to 0 decimals>"."""
    # TODO
    ...


if __name__ == "__main__":
    print("\n".join(review(BULLETS or ["Worked on an AI chatbot for a company using various technologies."])))
