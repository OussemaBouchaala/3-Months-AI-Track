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
    ...


def parse_judgment(reply):
    """Find the first {...} block in the reply (re.search(r"\{.*\}", reply, re.S)), json.loads it.
    Return {"correct": 0/1, "faithful": 0/1, "reason": str}. Values like true/"1" become 1.
    Anything unparseable -> {"correct": 0, "faithful": 0, "reason": "unparseable judge reply"}."""
    # TODO
    ...


def grade(item, answer, sources, call_model):
    """item: a test item dict. answer: the system's answer. sources: the text it was given.
    Unanswerable item (no source_ids): correct = faithful = 1 if IDK is in the answer else 0,
    reason "unanswerable", and NO model call.
    Answerable item but the system said IDK: correct = 0, faithful = 1, reason "false IDK", no model call.
    Otherwise: parse_judgment(call_model(judge_prompt(...)))."""
    # TODO
    ...


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
