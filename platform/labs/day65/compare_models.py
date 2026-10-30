"""Local model vs API model: which one should the agency use?

Averages hide where each model wins. Two better tools:

- **Per category**: the local model may be fine on fees and bad on Derja.
- **Pairwise judging with swapped positions**: a judge picks the better of two answers to
  the same question, twice, with A and B swapped. LLM judges favour whichever answer comes
  first; a win must survive the swap to count.

1. `per_category`: a metric's mean per question category.
2. `parse_preference`: read "A", "B" or "TIE" from the judge's text.
3. `debias`: combine the two orders into one fair outcome.
4. `win_rate`: one number for the whole comparison.
5. `paired`: who got right what the other got wrong.
"""
import re


def per_category(results, metric):
    """The mean of `metric` per category, categories sorted by name.

    Example:
        >>> R = [{"category": "fees", "correct": 1}, {"category": "fees", "correct": 0},
        ...      {"category": "deposit", "correct": 1}, {"category": "pets", "correct": 0}]
        >>> per_category(R, "correct")
        {'deposit': 1.0, 'fees': 0.5, 'pets': 0.0}
    """
    groups = {}
    for r in results:
        groups.setdefault(r["category"], []).append(r[metric])
    return {c: round(sum(v) / len(v), 3) for c, v in sorted(groups.items())}


def parse_preference(text):
    """The judge's verdict: `"A"`, `"B"` or `"TIE"`.

    1. The prompt asks for `[[A]]`, `[[B]]` or `[[TIE]]`: look for that first.
    2. Otherwise take the **last** standalone `A` / `B` / `TIE` word (the
       conclusion comes at the end). `\\b` means a whole word, so the "a"
       inside "answers" or "about" isn't read as a vote. `égalité` is a tie.
    3. Nothing found: `"TIE"` (don't invent a winner).

    Example:
        >>> parse_preference("I think [[B]].")
        'B'
        >>> parse_preference("Answer A cites the wrong clause, so B is better. Verdict: B")
        'B'
        >>> parse_preference("Égalité"), parse_preference("Both answers are about the same")
        ('TIE', 'TIE')
    """
    m = re.search(r"\[\[\s*(A|B|TIE)\s*\]\]", text, re.I)
    if m:
        return m.group(1).upper()
    found = re.findall(r"\b(A|B|TIE)\b|(égalité)", text, re.I)
    if not found:
        return "TIE"
    word, fr = found[-1]
    return "TIE" if fr else word.upper()


def debias(pref_ab, pref_ba):
    """Combine the two judgments into `"model1"`, `"model2"` or `"tie"`.

    First call: A = model 1, B = model 2. Second call: swapped. Model 1 wins
    only if it was picked both times ("A" then "B"). If the judge said "A"
    both times, it just likes the first position: that's a tie.

    Example:
        >>> debias("A", "B"), debias("B", "A"), debias("A", "A"), debias("TIE", "B")
        ('model1', 'model2', 'tie', 'tie')
    """
    if pref_ab == "A" and pref_ba == "B":
        return "model1"
    if pref_ab == "B" and pref_ba == "A":
        return "model2"
    return "tie"


def win_rate(outcomes, model="model1"):
    """`(wins + half the ties) / n`: 0.5 means "as good as the other".

    Example:
        >>> win_rate(["model1", "model1", "tie", "model2"])
        0.625
        >>> win_rate(["model1", "model1", "tie", "model2"], "model2"), win_rate([])
        (0.375, None)
    """
    if not outcomes:
        return None
    wins = sum(o == model for o in outcomes)
    ties = sum(o == "tie" for o in outcomes)
    return round((wins + 0.5 * ties) / len(outcomes), 3)


def paired(results1, results2, metric):
    """Compare two models question by question (matched by `id`, only
    questions both answered).

    `only1` / `only2` are the interesting cells: the same overall score can
    hide two models that fail on completely different questions.

    Example:
        >>> R1 = [{"id": "q1", "correct": 1}, {"id": "q2", "correct": 0}, {"id": "q3", "correct": 1}]
        >>> R2 = [{"id": "q1", "correct": 1}, {"id": "q2", "correct": 1}, {"id": "q3", "correct": 0}, {"id": "q9", "correct": 1}]
        >>> paired(R1, R2, "correct")
        {'n': 3, 'only1': 1, 'only2': 1, 'both': 1, 'neither': 0}
    """
    b = {r["id"]: r[metric] for r in results2}
    out = {"n": 0, "only1": 0, "only2": 0, "both": 0, "neither": 0}
    for r in results1:
        if r["id"] not in b:
            continue
        x, y = r[metric], b[r["id"]]
        out["n"] += 1
        out["both" if x and y else "only1" if x else "only2" if y else "neither"] += 1
    return out


JUDGE_PROMPT = """Two answers to the same client question, both supposed to use ONLY the sources.
Question: {question}
Sources:
{sources}

Answer A:
{a}

Answer B:
{b}

Which answer is more correct and better supported by the sources? Ignore length and style.
End with your verdict as [[A]], [[B]] or [[TIE]]."""


def compare(rows1, rows2, judge):
    """Judge every shared question twice (both orders) and debias.

    `rows1` / `rows2`: `{id: {"question", "sources", "answer"}}`;
    `judge(prompt) -> text`. Returns the list of outcomes.

    Example (a judge that always prefers the first answer):
        >>> rows = {"q1": {"question": "?", "sources": "", "answer": "x"}}
        >>> compare(rows, rows, lambda prompt: "[[A]]")
        ['tie']
    """
    outcomes = []
    for qid in sorted(set(rows1) & set(rows2)):
        q, a1, a2 = rows1[qid], rows1[qid]["answer"], rows2[qid]["answer"]
        ab = parse_preference(judge(JUDGE_PROMPT.format(question=q["question"], sources=q["sources"], a=a1, b=a2)))
        ba = parse_preference(judge(JUDGE_PROMPT.format(question=q["question"], sources=q["sources"], a=a2, b=a1)))
        outcomes.append(debias(ab, ba))
    return outcomes


def run_on_my_answers(local="answers_local.jsonl", api="answers_api.jsonl"):
    """The real comparison: your two answer files, judged by the Bench model.

    Example (note): needs both answer files and a model set in Bench.
        >>> run_on_my_answers()  # doctest: +SKIP
    """
    import json
    from bench_llm import current_model, get_client

    client = get_client()
    judge = lambda prompt: client.messages.create(model=current_model(), max_tokens=300, temperature=0,
                                                  messages=[{"role": "user", "content": prompt}]).content[0].text
    rows1 = {r["id"]: r for r in map(json.loads, open(local, encoding="utf-8"))}
    rows2 = {r["id"]: r for r in map(json.loads, open(api, encoding="utf-8"))}
    outcomes = compare(rows1, rows2, judge)
    print("local win rate vs API:", win_rate(outcomes), {o: outcomes.count(o) for o in set(outcomes)})
    print("correct per category, local:", per_category(list(rows1.values()), "correct"))
    print("correct per category, API:  ", per_category(list(rows2.values()), "correct"))
    print("paired:", paired(list(rows1.values()), list(rows2.values()), "correct"))


if __name__ == "__main__":
    from pathlib import Path
    if Path("answers_local.jsonl").exists() and Path("answers_api.jsonl").exists():
        run_on_my_answers()
    else:
        # Demo: 6 questions, recorded answers, and a fake judge with a position bias.
        cats = ["fees", "fees", "deposit", "derja", "derja", "pets"]
        local = {f"q{i}": {"id": f"q{i}", "category": c, "question": f"Q{i}", "sources": "", "answer": a, "correct": ok}
                 for i, (c, a, ok) in enumerate(zip(cats, ["good", "good", "good", "bad", "bad", "good"], [1, 1, 1, 0, 0, 1]))}
        api = {f"q{i}": {"id": f"q{i}", "category": c, "question": f"Q{i}", "sources": "", "answer": a, "correct": ok}
               for i, (c, a, ok) in enumerate(zip(cats, ["good", "ok", "good", "good", "good", "bad"], [1, 1, 1, 1, 1, 0]))}

        def judge(prompt):          # prefers the better answer; on equal answers, always says "A" (position bias)
            a = prompt.split("Answer A:\n")[1].split("\n")[0]
            b = prompt.split("Answer B:\n")[1].split("\n")[0]
            rank = {"bad": 0, "ok": 1, "good": 2}
            return "[[A]]" if rank[a] >= rank[b] else "Answer B is better supported. [[B]]"

        outcomes = compare(local, api, judge)
        print("outcomes:", outcomes)
        print("local win rate vs API:", win_rate(outcomes))
        print("per category, local:", per_category(local.values(), "correct"))
        print("per category, API:  ", per_category(api.values(), "correct"))
        print("paired:", paired(local.values(), api.values(), "correct"))
