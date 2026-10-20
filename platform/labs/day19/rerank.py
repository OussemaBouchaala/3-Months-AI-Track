# Retrieve wide (top 10), then rerank with a model that reads question AND passage together.
# Check uses fake scores. Run uses your ⚙ AI model as the reranker (slow but free).
import json
import re


def score_prompt(query, passage):
    """Ask the model to rate, from 0 to 10, how well the passage answers the query.
    It must reply with the number only. Include both the query and the passage."""
    # TODO
    ...


def parse_score(reply):
    """Take the first number in the reply (int or decimal, e.g. "8", "7.5", "Score: 9/10" -> 9.0).
    Clamp it to [0, 10]. No number -> 0.0. Return a float."""
    # TODO: re.search(r"\d+(\.\d+)?", reply)
    ...


def rerank(query, candidates, score_fn, top_n=3):
    """score_fn(query, text) -> float. Score every candidate's "text",
    return the top_n candidates by score, best first, each a NEW dict with an extra key "rerank_score".
    Don't modify the input dicts. Ties keep the original (retrieval) order."""
    # TODO
    ...


if __name__ == "__main__":
    import sys

    import numpy as np

    sys.path.append("../day16")
    from embed import embed, normalize, search
    from bench_llm import get_client, current_model

    chunks = json.load(open("../day15/chunks.json", encoding="utf-8"))
    matrix = np.load("../day16/embeddings.npy")
    client = get_client()

    def llm_score(query, text):
        msg = client.messages.create(model=current_model(), max_tokens=5, temperature=0,
                                     messages=[{"role": "user", "content": score_prompt(query, text)}])
        return parse_score(msg.content[0].text)

    q = "J'ai un chien, est-ce que je peux louer dans une résidence avec piscine ?"
    qv = normalize(embed([q]))[0]
    wide = [chunks[i] for i, _ in search(qv, matrix, k=10)]
    print("retrieval top 3:", [c["heading"] for c in wide[:3]])
    print("reranked top 3: ", [(c["heading"], c["rerank_score"]) for c in rerank(q, wide, llm_score)])
