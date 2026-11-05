# LLM-as-judge: is the answer correct, and is it faithful to the sources?
# Unanswerable questions don't need a judge: plain code checks for the IDK sentence.
import json
import re

IDK = "I don't know based on the documents."


def judge_prompt(question, expected, answer, sources):
    """Ask the judge to compare the answer with the expected answer and the sources.
    It must reply with JSON only: {"correct": 0 or 1, "faithful": 0 or 1, "reason": "<one sentence>"}
      correct  = the answer says the same thing as the expected answer (wording and language may differ)
      faithful = every claim in the answer is supported by the sources
    Include the question, the expected answer, the answer and the sources text."""
    # TODO
    return f"""You are an objective judge evaluating an AI system's answer.
Compare the generated answer against the question, the expected answer, and the sources.

Question: {question}
Expected Answer: {expected}
Generated Answer: {answer}
Sources: {sources}

Evaluate two things:
1. correct: 1 if the generated answer conveys the same meaning as the expected answer (wording and language can differ), else 0.
2. faithful: 1 if every claim in the generated answer is fully supported by the sources, else 0.

Reply with a JSON object ONLY, using this exact format:
{{"correct": 0 or 1, "faithful": 0 or 1, "reason": "<one sentence explanation>"}}"""



def parse_judgment(reply):
    """Find the first {...} block in the reply (re.search(r"{.*}", reply, re.S)), json.loads it.
    Return {"correct": 0/1, "faithful": 0/1, "reason": str}. Values like true/"1" become 1.
    Anything unparseable -> {"correct": 0, "faithful": 0, "reason": "unparseable judge reply"}."""
    # TODO
    m = re.search(r"\{.*\}", reply, re.S)
    if not m:
        return {"correct": 0, "faithful": 0, "reason": "unparseable judge reply"}
    try:
        d = json.loads(m.group())
        return {
            "correct": int(bool(int(d.get("correct", 0)))),
            "faithful": int(bool(int(d.get("faithful", 0)))),
            "reason": str(d.get("reason", ""))
        }
    except Exception:
        return {"correct": 0, "faithful": 0, "reason": "unparseable judge reply"}


def grade(item, answer, sources, call_model):
    """item: a test item dict. answer: the system's answer. sources: the text it was given.
    Unanswerable item (no source_ids): correct = faithful = 1 if IDK is in the answer else 0,
    reason "unanswerable", and NO model call.
    Answerable item but the system said IDK: correct = 0, faithful = 1, reason "false IDK", no model call.
    Otherwise: parse_judgment(call_model(judge_prompt(...)))."""
    # TODO
    if not item.get("source_ids"):
        ok = 1 if IDK in answer else 0
        return {"correct": ok, "faithful": ok, "reason": "unanswerable"}
    
    if answer.strip() == IDK:
        return {"correct": 0, "faithful": 1, "reason": "false IDK"}
        
    prompt = judge_prompt(item["question"], item.get("expected"), answer, sources)
    return parse_judgment(call_model(prompt))


if __name__ == "__main__":
    import sys

    sys.path.append("../day18")
    from bench_llm import get_client, current_model

    client = get_client()

    def call_model(prompt):
        msg = client.messages.create(model=current_model(), max_tokens=150, temperature=0,
                                     messages=[{"role": "user", "content": prompt}])
        return msg.content[0].text

    item = {"question": "Le propriétaire peut-il augmenter le loyer de 8% ?",
            "answer": "Non: pas la première année, puis 5% maximum par an.", "source_ids": ["c6"]}
    sources = "Le loyer ne peut pas être augmenté pendant la première année. Ensuite, max 5% par an."
    for answer in ["Non, au maximum 5% par an après la première année [1].",
                   "Oui, 8% est autorisé si le propriétaire prévient un mois avant [1].",
                   "No, increases are capped at 5% a year, and only after the first year [1]."]:
        print(grade(item, answer, sources, call_model), "<-", answer)
