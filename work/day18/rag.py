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
    parts = []
    for i, chunk in enumerate(chunks, 1):
        heading = chunk.get("heading", "")
        text = chunk.get("text", "")
        # [1] Heading
        # Text
        parts.append(f"[{i}] {heading}\n{text}")
    return "\n\n".join(parts)

def build_prompt(question, chunks):
    """The full prompt. It must contain:
    - the rules: answer ONLY from the sources; cite every fact like [1] or [2];
      if the sources don't contain the answer, reply exactly IDK; answer in the language of the question
    - the numbered sources (format_context)
    - the question"""
    context = format_context(chunks)
    rules = (
        f"Answer ONLY from the provided sources.\n"
        f"Cite every fact using the source number in brackets, e.g., [1] or [2].\n"
        f"If the answer is not in the sources, reply exactly: {IDK}\n"
        f"Answer in the language of the question.\n"
    )
    return f"{rules}\nSources:\n{context}\n\nQuestion: {question}"


def parse_citations(answer):
    """Every number cited as [n] in the answer, unique and sorted. "[2] and [1][2]" -> [1, 2]."""
    matches = re.findall(r"\[(\d+)\]", answer)
    # Convert to int, make unique, and sort
    return sorted(set(int(m) for m in matches))


def answer(question, retrieve, call_model, k=4):
    """retrieve(question, k) -> list of chunk dicts; call_model(prompt) -> text.
    Return {"answer": text, "sources": [ids of the chunks cited], "valid": bool}.
    valid is False when the answer cites a number that isn't a source (e.g. [7] with 4 sources),
    or when it cites nothing and isn't IDK."""
    
    # 1. Retrieve relevant chunks
    chunks = retrieve(question, k)
    
    # 2. Build the prompt using the retrieved chunks
    prompt = build_prompt(question, chunks)
    
    # 3. Call the model
    raw_answer = call_model(prompt)
    
    # 4. Parse citations from the model's answer
    cited_nums = parse_citations(raw_answer)
    
    # 5. Map cited numbers back to chunk IDs
    # Note: Cited numbers are 1-indexed corresponding to the order in `chunks`
    cited_ids = []
    for num in cited_nums:
        if 1 <= num <= len(chunks):
            cited_ids.append(chunks[num - 1]["id"])
        else:
            # This chunk doesn't exist in the retrieved set -> invalid citation
            # We still include it in the list structure if required, but mark valid as False later.
            # Usually, we just want the IDs of *valid* sources cited, or we flag the whole thing as invalid.
            # The spec says: "valid is False when the answer cites a number that isn't a source"
            # It doesn't explicitly say what to put in "sources" in that case, 
            # but typically we might still return the valid ones or an empty list. 
            # Let's assume we return the IDs corresponding to valid citations, 
            # and the 'valid' flag handles the error.
            pass 

    # Check validity
    valid = True
    # Condition 1: Cites a number that isn't a source
    if len(cited_nums) != len(cited_ids):
        valid = False
        
    # Condition 2: Cites nothing and isn't IDK
    if not cited_ids and IDK not in raw_answer:
        valid = False

    return {
        "answer": raw_answer,
        "sources": cited_ids,
        "valid": valid
    }


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