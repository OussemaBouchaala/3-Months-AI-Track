# Retrieval-augmented generation: find the right chunks, then answer ONLY from them, with citations.
# Check uses a fake retriever and a fake model. Run uses Ollama embeddings + your ⚙ AI model.
import json
import re

IDK = "I don't know based on the documents."


def format_context(chunks):
    """Number the chunks for the model, starting at 1:
    [1] <heading>
    <text>

    [2] <heading>
    ...
    (one blank line between sources)"""
    # TODO
    ...


def build_prompt(question, chunks):
    """The full prompt. It must contain:
    - the rules: answer ONLY from the sources; cite every fact like [1] or [2];
      if the sources don't contain the answer, reply exactly IDK; answer in the language of the question
    - the numbered sources (format_context)
    - the question"""
    # TODO
    ...


def parse_citations(answer):
    """Every number cited as [n] in the answer, unique and sorted. "[2] and [1][2]" -> [1, 2]."""
    # TODO: re.findall(r"\[(\d+)\]", answer)
    ...


def answer(question, retrieve, call_model, k=4):
    """retrieve(question, k) -> list of chunk dicts; call_model(prompt) -> text.
    Return {"answer": text, "sources": [ids of the chunks cited], "valid": bool}.
    valid is False when the answer cites a number that isn't a source (e.g. [7] with 4 sources),
    or when it cites nothing and isn't IDK."""
    # TODO
    ...


if __name__ == "__main__":
    import sys

    import numpy as np

    sys.path.append("../day16")
    from embed import embed, normalize, search   # your Tuesday code
    from bench_llm import get_client, current_model

    chunks = json.load(open("../day15/chunks.json", encoding="utf-8"))
    matrix = np.load("../day16/embeddings.npy")
    client = get_client()

    def retrieve(question, k):
        qv = normalize(embed([question]))[0]
        return [chunks[i] for i, _ in search(qv, matrix, k)]

    def call_model(prompt):
        msg = client.messages.create(model=current_model(), max_tokens=300, temperature=0,
                                     messages=[{"role": "user", "content": prompt}])
        return msg.content[0].text

    for q in ["Can my landlord raise the rent by 8% next year?",
              "Combien coûte une estimation si je ne mets pas mon bien en vente ?",
              "هل يمكن زيارة العقار يوم الأحد؟",
              "Does the agency sell cars?"]:
        r = answer(q, retrieve, call_model)
        print(f"Q: {q}\nA: {r['answer']}\n   sources={r['sources']} valid={r['valid']}\n")
