# Local model vs API model. Averages hide where each one wins; pairwise judging with swapped positions
# tells you which answer is better on the SAME question, without the judge's bias for "the first one".
import re


def per_category(results, metric):
    """results: [{"id", "category", metric: 0/1 or float}, ...] -> {category: mean rounded to 3}, categories sorted."""
    # TODO
    ...


def parse_preference(text):
    """The judge's verdict: "A", "B" or "TIE". Accept "[[A]]", "Verdict: B", "answer a is better", "tie", "égalité".
    Look for [[X]] first; otherwise the LAST standalone A / B / TIE word (case-insensitive; "égalité" counts as TIE).
    Nothing found -> "TIE"."""
    # TODO
    ...


def debias(pref_ab, pref_ba):
    """The judge saw (A=model1, B=model2) then the swapped order (A=model2, B=model1).
    Return "model1", "model2" or "tie": a model wins only if it wins in BOTH orders; otherwise "tie"."""
    # TODO
    ...


def win_rate(outcomes, model="model1"):
    """(wins + 0.5 * ties) / n, rounded to 3, for model. Empty -> None."""
    # TODO
    ...


def paired(results1, results2, metric):
    """Compare on the questions both have (by id): {"n", "only1" (1 right, 2 wrong), "only2", "both", "neither"}.
    metric values are 0/1."""
    # TODO
    ...


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


if __name__ == "__main__":
    import json
    from bench_llm import current_model, get_client

    client = get_client()
    judge = lambda prompt: client.messages.create(model=current_model(), max_tokens=300, temperature=0,
                                                  messages=[{"role": "user", "content": prompt}]).content[0].text
    rows1 = {r["id"]: r for r in map(json.loads, open("answers_local.jsonl", encoding="utf-8"))}
    rows2 = {r["id"]: r for r in map(json.loads, open("answers_api.jsonl", encoding="utf-8"))}
    outcomes = []
    for qid in sorted(set(rows1) & set(rows2)):
        q, a1, a2 = rows1[qid], rows1[qid]["answer"], rows2[qid]["answer"]
        ab = parse_preference(judge(JUDGE_PROMPT.format(question=q["question"], sources=q["sources"], a=a1, b=a2)))
        ba = parse_preference(judge(JUDGE_PROMPT.format(question=q["question"], sources=q["sources"], a=a2, b=a1)))
        outcomes.append(debias(ab, ba))
    print("local win rate vs API:", win_rate(outcomes), {o: outcomes.count(o) for o in set(outcomes)})
    print("correct per category, local:", per_category(list(rows1.values()), "correct"))
    print("correct per category, API:  ", per_category(list(rows2.values()), "correct"))
    print("paired:", paired(list(rows1.values()), list(rows2.values()), "correct"))
