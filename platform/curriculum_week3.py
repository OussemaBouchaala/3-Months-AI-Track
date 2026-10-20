"""Week 3: RAG from scratch (Oct 19-25, 2026).

The corpus is labs/day15/handbook.md, a fictional trilingual agency handbook, so the
pipeline works before the real Arabic corpus arrives in Week 6."""
from lab_files import lab

DAY15 = {
    "id": "w3d1", "folder": "day15", "notes_task": 3, "date": "2026-10-19", "weekday": "Mon",
    "title": "Chunking", "minutes": 75,
    "why": "Retrieval can only find what you cut well. Bad chunks are the most common reason RAG fails.",
    "lesson": r"""
:::hook
A client asks the agency's chatbot: "How much is the deposit?" The answer is in the handbook, in one sentence in the middle of page 3. The model can't read the whole handbook for every question (too slow, too expensive), so you give it **the right few paragraphs**. Before you can find the right paragraph, you have to decide what a paragraph *is*. That's chunking.
:::

## Why cut documents at all

RAG = **R**etrieve the relevant pieces, then let the model **G**enerate an answer from them. The pieces are **chunks**. Each chunk becomes one vector (tomorrow), so a chunk should be about **one thing**.

:::analogy
A chunk is an index card in a library catalogue. One card per book is too coarse ("this book mentions deposits somewhere"). One card per word is useless. One card per section, with its title written on top, is what a librarian would do.
:::

:::check
? A chunk mixes the "deposit" policy and the "pets" policy. What goes wrong?
- Nothing, the model reads both
* Its vector is a blur of two meanings, so it matches neither question well
- It costs fewer tokens
> One vector per chunk means one meaning per chunk. Mixed chunks rank lower for both topics.
:::

## Fixed-size chunks with overlap

The simplest method: cut every N characters. A sentence cut in half loses its meaning, so neighbouring chunks **overlap**.

```python
text = "Visits are free. Book 24 hours in advance. An agent always comes with you."
size, overlap = 30, 10
step = size - overlap
for start in range(0, len(text), step):
    print(repr(text[start:start + size]))
    if start + size >= len(text):
        break
```

:::predict With size 400 and overlap 80, how far apart do two chunks start? How many chunks for a 1,000-character text?
---
They start **320** characters apart (400 - 80). Starts at 0, 320, 640: the chunk at 640 reaches 1,040 ≥ 1,000, so it's the last. **3 chunks**.
:::

## Chunk by structure

Documents written by people already have structure: headings. Cutting on `## ` gives one chunk per topic, and you keep the heading in the chunk text, because "Augmentation du loyer" tells the retriever a lot.

:::key
Default recipe: split on headings; if a section is too long, cut it with fixed size + overlap; always keep the heading in each piece.
:::

:::mistake
Chunks that are too small ("Max 5%.") lose their context: 5% of what? Chunks that are too big (a whole chapter) dilute the meaning and waste tokens. For text like the handbook, 200-800 characters per chunk is a good start. You'll **measure** the best size in Week 4, not guess it.
:::

:::reveal What about tables and PDFs?
Tables lose their meaning when cut row by row: keep a table in one chunk with its header. PDFs need parsing first (Week 8). Today the input is clean Markdown so you can focus on the idea.
:::

## Lock it in

:::cards
What does RAG stand for? :: Retrieval-Augmented Generation: find relevant chunks, then answer from them.
Why overlap? :: So an idea cut at a boundary still appears whole in one chunk.
Step between fixed chunks? :: size - overlap.
Why keep the heading in each chunk? :: It names the topic, which helps retrieval match the question.
Best chunk size? :: Measure it (Week 4). Start around 200-800 characters for prose.
:::

:::explain Explain to a colleague why "one chunk per heading" beats "one chunk per 400 characters" for the agency handbook, and when it wouldn't.
:::
""",
    "files": [
        lab("day15", "handbook.md"),
        lab("day15", "chunking.py", task=[1, 2]),
    ],
    "tasks": [
        "Read the [Pinecone guide to chunking strategies](https://www.pinecone.io/learn/chunking-strategies/)",
        "chunking.py: fixed-size chunks with overlap",
        "chunking.py: chunks by heading, saved to chunks.json",
        "Notes: which chunking you'd use for the handbook, and why",
    ],
    "done_when": "chunks.json holds 14 chunks, one per handbook section.",
    "resources": [{"label": "Pinecone: chunking strategies", "url": "https://www.pinecone.io/learn/chunking-strategies/"}],
    "quiz": [
        {"q": "Fixed chunks of 500 characters with 100 overlap. Where does the third chunk start?", "options": ["500", "800", "1000", "900"], "answer": 1,
         "explain": "Step = 500 - 100 = 400. Starts: 0, 400, 800."},
        {"q": "Why keep the section heading inside every chunk?", "options": ["It makes chunks shorter", "It names the topic, so retrieval matches better", "Postgres requires it", "It removes the need for overlap"], "answer": 1,
         "explain": "A piece of a long section may never mention its topic; the heading does."},
    ],
}

DAY16 = {
    "id": "w3d2", "folder": "day16", "date": "2026-10-20", "weekday": "Tue",
    "title": "Multilingual embeddings", "minutes": 75,
    "why": "Your clients ask in Arabic, French and English about documents in all three. The embedding model is what makes that work.",
    "lesson": r"""
:::hook
A client in Tunis types "كم قيمة الضمان؟". The answer sits in a section written in Arabic, but the next client asks the same thing in French, and the next in English. Keyword search would need three dictionaries. A **multilingual embedding model** puts all three questions at the same spot on the map, next to the deposit section.
:::

## From text to vector

On Sunday you computed cosine similarity on 3-number toy vectors. A real embedding model outputs **1024 numbers** per text (bge-m3), trained so that texts with the same meaning point in the same direction, whatever the language.

:::analogy
Think of a translator who doesn't write the translation, only a GPS position for the *idea*. "Deposit", "caution" and "الضمان" all get the same coordinates. Searching = finding the nearest coordinates.
:::

## Which model?

- **bge-m3** (BAAI): strong on Arabic, French, English; 1024 dimensions; runs in Ollama (`ollama pull bge-m3`).
- **multilingual-e5** (Microsoft): also good; it expects the prefixes `query: ` and `passage: ` in front of the text.

:::mistake
Embedding the documents with one model and the questions with another. The two maps have different coordinates, so similarities are meaningless. **Same model for both, always**, and re-embed everything if you switch.
:::

## Normalize once, then dot product

If every vector has length 1, cosine similarity is just the dot product, and a whole search is one matrix multiplication.

```python
import numpy as np

m = np.array([[3.0, 4.0], [1.0, 0.0], [0.0, 2.0]])
m = m / np.linalg.norm(m, axis=1, keepdims=True)    # every row now has length 1
q = np.array([1.0, 1.0]); q = q / np.linalg.norm(q)
scores = m @ q                                       # 3 cosine similarities at once
print(scores.round(3), "best:", int(np.argmax(scores)))
```

:::predict 14 chunks, 1024 dimensions. What is the shape of `matrix @ query` and what does each number mean?
---
Shape **(14,)**: one cosine similarity per chunk. `np.argsort(-scores)[:3]` gives the 3 best chunk indexes.
:::

:::check
? You send all 10,000 chunks of a big corpus in one embedding request. What's the risk?
- The vectors come back less accurate
* The request is too big: it times out or is rejected, and you lose everything
- Ollama ignores the extra texts
> Batches of 16-64 texts keep each request small, and one failure costs one batch.
:::

:::reveal Why 1024 numbers and not 3?
Meaning has many independent directions: topic, tone, language, negation, numbers... Three numbers can't separate "rent increase" from "rent decrease". A thousand can, mostly. Bigger isn't always better: storage and search cost grow with dimensions.
:::

:::cards
What does an embedding model output? :: A fixed-size vector (bge-m3: 1024 numbers) per text.
Same model for docs and questions? :: Always. Different models = different maps.
Why normalize? :: Then cosine similarity = dot product, and search = one matrix multiplication.
Why batch embedding calls? :: Small requests don't time out, and a failure costs one batch.
e5's special requirement? :: Prefixes "query: " and "passage: ".
:::

:::explain Explain why a French question can find an Arabic paragraph with embeddings but not with keyword search.
:::
""",
    "files": [
        lab("day16", "embed.py", task=[1, 2]),
    ],
    "tasks": [
        "Pull the model: `ollama pull bge-m3` ([model page](https://ollama.com/library/bge-m3))",
        "embed.py: embed the 14 chunks in batches, save embeddings.npy",
        "Search the same question in English, French and Arabic",
        "Read the [bge-m3 model card](https://huggingface.co/BAAI/bge-m3) (what it supports, max length)",
    ],
    "done_when": "All three versions of the deposit question find الضمان in their top 3.",
    "resources": [{"label": "bge-m3 on Hugging Face", "url": "https://huggingface.co/BAAI/bge-m3"},
                  {"label": "Ollama embeddings API", "url": "https://github.com/ollama/ollama/blob/main/docs/api.md#generate-embeddings"}],
    "quiz": [
        {"q": "Rows are normalized. What is matrix @ query?", "options": ["Euclidean distances", "Cosine similarities", "Token counts", "Probabilities that sum to 1"], "answer": 1,
         "explain": "For unit vectors, the dot product is exactly the cosine."},
        {"q": "You switch from bge-m3 to multilingual-e5. What must you do?", "options": ["Nothing", "Re-embed only the new documents", "Re-embed every document with e5", "Normalize again"], "answer": 2,
         "explain": "Vectors from different models live on different maps."},
    ],
}

DAY17 = {
    "id": "w3d3", "folder": "day17", "date": "2026-10-21", "weekday": "Wed",
    "title": "Vector search with pgvector", "minutes": 75,
    "why": "A NumPy matrix lives in memory and dies with the script. A database keeps vectors next to their text and metadata.",
    "lesson": r"""
:::hook
Your NumPy search works on 14 chunks. The agency has 3,000 documents, a website that restarts every night, and a manager who wants to filter by city. You need the vectors **stored**, **searchable with SQL**, and next to the text and metadata. That's pgvector: Postgres with a vector column.
:::

## A vector column

```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE chunks (
    id text PRIMARY KEY,
    heading text,
    content text,
    embedding vector(1024)
);
```

:::analogy
A normal table is a filing cabinet sorted by name. pgvector adds a drawer sorted by **meaning**: you hand it a question's vector and it gives back the closest files, with all their labels attached.
:::

## Three distance operators

- `<->` Euclidean distance
- `<#>` negative inner product
- `<=>` **cosine distance** = 1 - cosine similarity. Use this one with normalized text embeddings.

:::predict A chunk has cosine similarity 0.83 with the question. What does `embedding <=> query` return? And should you sort ASC or DESC?
---
Distance = 1 - 0.83 = **0.17**. Smaller distance = closer, so `ORDER BY embedding <=> query` **ascending** (the default) puts the best first. Show `1 - distance` to get back the similarity.
:::

```python
import numpy as np
a, q = np.array([0.6, 0.8]), np.array([1.0, 0.0])
cos = a @ q / (np.linalg.norm(a) * np.linalg.norm(q))
print("similarity", round(cos, 2), "| pgvector <=> distance", round(1 - cos, 2))
```

## Upserts: run it twice safely

`INSERT ... ON CONFLICT (id) DO UPDATE` inserts new chunks and updates existing ones. Re-running your indexing script never fails and never duplicates.

:::check
? Your script crashes at chunk 900 of 3,000. You fix it and run it again. With a plain INSERT, what happens?
- It continues from chunk 900
* It fails on chunk 0: duplicate primary key
- It silently creates duplicates
> With `ON CONFLICT (id) DO UPDATE`, the rerun just overwrites the first 900 and continues.
:::

## Indexes: exact vs approximate

Without an index, Postgres compares the query to every row (exact, fine up to ~100k rows). An **HNSW** index finds *almost* the nearest neighbours much faster on millions of rows.

:::mistake
Creating an HNSW index with `vector_l2_ops` and then searching with `<=>`. The index only serves the operator it was built for: use `vector_cosine_ops` with `<=>`, or the query silently scans every row.
:::

:::reveal Why "approximate" is acceptable
HNSW might return the 2nd and 4th best instead of the 2nd and 3rd. For RAG, the top 10 still contains the right chunk, and a reranker (Friday) fixes the order. A 100x speedup is worth a tiny recall loss; you'll measure recall@k in Week 4.
:::

:::cards
pgvector's cosine distance operator? :: <=>
Similarity from distance? :: 1 - distance.
Sort order for nearest first? :: ORDER BY embedding <=> query (ascending).
Why ON CONFLICT DO UPDATE? :: Re-running the indexer updates instead of failing.
HNSW? :: An approximate nearest-neighbour index: much faster, tiny recall loss.
:::

:::explain Explain to a backend developer why storing vectors in Postgres can be simpler than a separate vector database for this project.
:::
""",
    "files": [
        lab("day17", "docker-compose.yml", task=0),
        lab("day17", "pg_store.py", task=[1, 2]),
    ],
    "tasks": [
        "Postgres + pgvector running with Docker Compose",
        "pg_store.py: table, upsert, HNSW index",
        "Search in SQL; the ranking matches NumPy's",
        "Read the [pgvector README](https://github.com/pgvector/pgvector#querying): operators and HNSW",
    ],
    "done_when": "The 14 chunks are in Postgres and a SQL query returns the same top 3 as NumPy.",
    "resources": [{"label": "pgvector README", "url": "https://github.com/pgvector/pgvector"},
                  {"label": "psycopg 3 basics", "url": "https://www.psycopg.org/psycopg3/docs/basic/usage.html"}],
    "quiz": [
        {"q": "Which pgvector operator matches cosine similarity on normalized embeddings?", "options": ["<->", "<#>", "<=>", "@@"], "answer": 2,
         "explain": "<=> is cosine distance; ORDER BY it ascending."},
        {"q": "Why use ON CONFLICT (id) DO UPDATE when indexing?", "options": ["It's faster", "Re-runs update rows instead of failing on duplicate ids", "It builds the HNSW index", "It normalizes vectors"], "answer": 1,
         "explain": "Idempotent indexing: run it as often as you like."},
    ],
}

DAY18 = {
    "id": "w3d4", "folder": "day18", "notes_task": 3, "date": "2026-10-22", "weekday": "Thu",
    "title": "Generate answers with citations", "minutes": 75,
    "why": "Retrieval finds the chunks; the answer must come from them, and say where, or nobody can trust it.",
    "lesson": r"""
:::hook
A client asks: "Can my landlord raise the rent by 8%?" A plain chatbot answers confidently from its general knowledge of French law: wrong country, wrong rule. Your RAG system answers: "No, at most 5% per year after the first year [2]", and the [2] links to the agency's own policy. That bracket is the difference between a toy and a tool.
:::

## The RAG prompt

Three parts, in this order: **rules**, **numbered sources**, **question**.

```python
chunks = [{"heading": "Visits", "text": "Visits are free, Monday to Saturday."},
          {"heading": "Augmentation du loyer", "text": "Pas d'augmentation la première année, puis 5% max par an."}]
sources = "\n\n".join(f"[{i}] {c['heading']}\n{c['text']}" for i, c in enumerate(chunks, 1))
prompt = ("Answer ONLY from the sources. Cite every fact like [1]. "
          "If the sources don't contain the answer, reply exactly: I don't know based on the documents.\n\n"
          f"Sources:\n{sources}\n\nQuestion: Can my landlord raise the rent by 8%?")
print(prompt)
```

:::analogy
You're an exam proctor handing a student an open-book exam with **only these pages**. "Answer from these pages, write the page number next to each claim, and if it's not in them, write 'not in the material'." The page numbers let you grade the answer in seconds.
:::

## "I don't know" is a feature

:::predict A client asks "Does the agency sell cars?" The retriever still returns the 4 "closest" chunks (visits, fees...). What does a model do without the IDK rule?
---
It often **invents** a plausible answer from the unrelated chunks or from its training ("Yes, contact us for vehicle sales"). Retrieval always returns *something*; only the rule + an exact IDK sentence lets the model, and your code, say "not found".
:::

:::key
An exact IDK sentence is a contract with your code: `if IDK in answer` is reliable; "the model said something like it doesn't know" is not.
:::

## Check the citations in code

Parse `[n]` from the answer and check each `n` is a real source. A citation `[7]` with 4 sources is a hallucinated reference: flag it.

```python
import re
answer, n_sources = "No, max 5% per year [2], see also [7].", 4
cited = sorted({int(n) for n in re.findall(r"\[(\d+)\]", answer)})
print(cited, "valid:", all(1 <= n <= n_sources for n in cited))
```

:::check
? The model answers correctly but cites nothing. Should your code accept it?
- Yes, the answer is right
* No: without a citation nobody can verify it; flag it as invalid
- Only if the question was in English
> You can't tell a correct uncited answer from a confident hallucination. Require citations (or IDK).
:::

:::mistake
Putting the question **before** a long list of sources. Models pay most attention to the start and the end of the prompt: rules first, sources in the middle, question last, right where the answer begins.
:::

:::cards
3 parts of a RAG prompt, in order? :: Rules, numbered sources, question.
Why an exact IDK sentence? :: So code can detect "not found" reliably.
Citation [7] with 4 sources? :: Invalid: a hallucinated reference.
Uncited answer? :: Invalid: unverifiable.
Answer language? :: The language of the question.
:::

:::explain Explain to the agency manager why the bot sometimes says "I don't know" even though the model "knows" about real estate in general.
:::
""",
    "files": [
        lab("day18", "rag.py", task=[0, 1]),
    ],
    "tasks": [
        "rag.py: numbered sources, strict prompt, citations parsed",
        "Answer 4 questions (EN, FR, AR, and one the handbook can't answer)",
        "Read [Anthropic: reduce hallucinations](https://docs.anthropic.com/en/docs/test-and-evaluate/strengthen-guardrails/reduce-hallucinations)",
        "Notes: one answer that was wrong or badly cited, and why",
    ],
    "done_when": "Every answer cites real sources, and the car question gets the IDK sentence.",
    "resources": [{"label": "Reduce hallucinations (Anthropic docs)", "url": "https://docs.anthropic.com/en/docs/test-and-evaluate/strengthen-guardrails/reduce-hallucinations"}],
    "quiz": [
        {"q": "The answer cites [5] but only 3 sources were given. What do you do?", "options": ["Accept it", "Mark the answer invalid: the citation doesn't exist", "Retrieve 5 sources next time", "Remove the citation and accept"], "answer": 1,
         "explain": "A citation to a non-existent source is a hallucination signal."},
        {"q": "Best order for the RAG prompt?", "options": ["Question, sources, rules", "Sources, question, rules", "Rules, sources, question", "Order doesn't matter"], "answer": 2,
         "explain": "Rules up front, the question last, right before the answer."},
    ],
}

DAY19 = {
    "id": "w3d5", "folder": "day19", "notes_task": 2, "date": "2026-10-23", "weekday": "Fri",
    "title": "Add a reranker", "minutes": 75,
    "why": "Embeddings are fast but shallow. A reranker reads the question and passage together and fixes the order.",
    "lesson": r"""
:::hook
"J'ai un chien, est-ce que je peux louer dans une résidence avec piscine ?" The embedding search returns "Frais d'agence pour la location" first, because "louer" and "location" are close. The right answer, "Animaux de compagnie", is 4th. The model only sees the top 3, so it answers "I don't know". A **reranker** reads each candidate *with* the question and pushes the pets section to the top.
:::

## Two kinds of models

- **Bi-encoder** (your embedding model): embeds the question and each chunk *separately*. Chunk vectors are computed once, so search is instant. But the question never "meets" the chunk.
- **Cross-encoder** (a reranker): reads `(question, chunk)` *together* and outputs a relevance score. Much more accurate, much slower: one model call per pair.

:::analogy
Recruiting. The bi-encoder is the HR filter that reads CVs once and keeps 20 with matching profiles, instantly. The cross-encoder is the interview: you put each candidate in front of *this* job and judge the fit. You can't interview 3,000 people, but you can interview 10.
:::

## Retrieve wide, rerank narrow

The standard pipeline: retrieve **top 10-50** with vectors (cheap), rerank them (expensive per pair, but only 10-50 pairs), send the **top 3-5** to the generator.

:::predict Reranking 10 candidates with a cross-encoder takes about 0.2 s on a laptop. How long would reranking all 3,000 chunks take, and why does that matter?
---
About **60 s** (3,000 / 10 x 0.2 s). Way too slow for a chat. That's why the reranker only sees the top candidates from the fast retriever.
:::

## Your reranker today

Production systems use a dedicated cross-encoder like **bge-reranker-v2-m3** (multilingual). Today you use your ⚙ AI model as a 0-10 judge: same idea, no new install.

```python
import re

def parse_score(reply):
    m = re.search(r"\d+(\.\d+)?", reply)
    return 0.0 if not m else min(10.0, max(0.0, float(m.group())))

for reply in ["8", "Score: 7.5/10", "I would say 12", "No idea"]:
    print(repr(reply), "->", parse_score(reply))
```

:::check
? Your LLM reranker sometimes replies "Relevance: high". What should parse_score return?
- Crash, so you notice
* 0.0, the safe default, and you log it
- 10.0
> One odd reply shouldn't crash a request. Default low, log it, and look at the logs later.
:::

:::mistake
Reranking with an LLM at temperature 1.0. Scores then change between runs and the ranking jumps around. Judges and rerankers: **temperature 0**.
:::

:::cards
Bi-encoder vs cross-encoder? :: Bi: question and doc embedded separately (fast). Cross: read together (accurate, slow).
Typical pipeline? :: Retrieve top 10-50, rerank, keep top 3-5.
Why not rerank everything? :: One model call per pair: far too slow.
A multilingual cross-encoder? :: bge-reranker-v2-m3.
Reranker temperature? :: 0.
:::

:::explain Explain why a reranker can fix a ranking that the embedding search got wrong, using the dog-and-pool example.
:::
""",
    "files": [
        lab("day19", "rerank.py", task=[0, 1]),
    ],
    "tasks": [
        "rerank.py: score prompt, robust score parsing, rerank top 10",
        "Compare top 3 before and after reranking on 3 questions",
        "Notes: did reranking change the answer? How much slower was it?",
        "Read the [bge-reranker-v2-m3 card](https://huggingface.co/BAAI/bge-reranker-v2-m3)",
    ],
    "done_when": "The pets question gets the pets section in its top 3 after reranking.",
    "resources": [{"label": "SBERT: retrieve & re-rank", "url": "https://sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html"}],
    "quiz": [
        {"q": "Why not use the cross-encoder for the whole search?", "options": ["It's less accurate", "It needs one model call per (question, chunk) pair: too slow at scale", "It can't read Arabic", "It needs a GPU"], "answer": 1,
         "explain": "It only scales to a short candidate list."},
        {"q": "A typical rerank pipeline sends how many chunks to the generator?", "options": ["All of them", "The top 3-5 after reranking", "Exactly 1", "The top 50"], "answer": 1,
         "explain": "Retrieve wide (10-50), rerank, keep a few."},
    ],
}

DAY20 = {
    "id": "w3d6", "folder": "day20", "notes_task": 2, "date": "2026-10-24", "weekday": "Sat",
    "title": "Hybrid search, end to end", "minutes": 180,
    "why": "Vectors miss exact terms like 'CIN' or '150 TND'. Keywords miss meaning. Together they cover each other.",
    "lesson": r"""
:::hook
A client types "CIN passport payslips". The vector search returns "Buying as a foreigner" (passport, foreigner: close meaning). The right section, "Documents required to rent", contains those **exact words**. Embeddings blur exact terms, codes, numbers and names. Old-school keyword search nails them. Today you use both.
:::

## BM25 in one picture

BM25 scores a document by the query words it contains, with three ideas:
1. **Rare words matter more** (idf): "CIN" appears in 1 section, "the" in all of them.
2. **Repeating a word helps, but less and less** (tf saturates, controlled by k1).
3. **Long documents are penalised a bit** (b), since they contain everything.

```python
import math
N = 14                       # sections in the handbook
for word, df in [("cin", 1), ("loyer", 3), ("the", 14)]:
    idf = math.log((N - df + 0.5) / (df + 0.5) + 1)
    print(f"{word:<6} in {df:>2} docs -> idf {idf:.2f}")
```

:::predict A query word appears in every document. How much does it change the ranking?
---
Almost nothing: its idf is close to 0 (`ln(0.5/14.5 + 1)` ≈ 0.03), so every document gets the same tiny bonus. That's how BM25 ignores "the", "de", "في" without a stopword list.
:::

## Reciprocal Rank Fusion

BM25 scores (0 to ~10) and cosine (0 to 1) aren't comparable, so don't add them. **RRF** adds rank points instead: each list gives `1 / (60 + rank)`. Documents near the top of *both* lists win.

:::analogy
Two critics rate films on different scales (stars and percentages). Instead of converting scales, you ask each for their ranking and give points by position. A film that's 2nd for both beats a film that's 1st for one and 40th for the other.
:::

:::check
? Why the constant 60 in 1/(60 + rank)?
- It's the number of documents
* It flattens the curve so rank 1 doesn't crush rank 2, 3...
- Postgres requires it
> With k = 0, rank 1 gets 1.0 and rank 2 gets 0.5: one list dominates. k = 60 is the value from the original paper and works well in practice.
:::

:::key
Production RAG usually looks like: BM25 + vectors → RRF → rerank top 20 → top 4 to the model with citations. You've now built every box.
:::

:::mistake
Tokenizing Arabic with `.split()` and lowercase only. "الضمان" and "والضمان" ("and the deposit") become different words. `\w+` is a start; Week 6 adds Arabic normalization and light stemming.
:::

:::cards
idf in one sentence? :: Rare words count more; words in every document count almost nothing.
Why not add BM25 and cosine scores? :: Different scales; fuse ranks instead.
RRF formula? :: Sum over lists of 1 / (k + rank), k = 60, rank from 1.
When does keyword search win? :: Exact terms: codes, IDs, numbers, names.
When do vectors win? :: Paraphrases and other languages.
:::

:::explain Explain hybrid search to a non-technical manager using one question where keywords win and one where vectors win.
:::
""",
    "files": [
        lab("day20", "hybrid.py", task=[0, 1]),
    ],
    "tasks": [
        "hybrid.py: BM25 and Reciprocal Rank Fusion",
        "Compare keyword, vector and hybrid on 3 queries",
        "Notes: which query type each method wins",
        "Run the whole chain on 10 questions: hybrid → rerank → cited answer",
    ],
    "done_when": "Hybrid ranks the right section in the top 3 for both the exact-term and the paraphrased query.",
    "resources": [{"label": "RRF paper (Cormack et al., 2009)", "url": "https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf"},
                  {"label": "BM25 explained (Elastic)", "url": "https://www.elastic.co/blog/practical-bm25-part-2-the-bm25-algorithm-and-its-variables"}],
    "quiz": [
        {"q": "Which query does BM25 handle better than embeddings?", "options": ["'how do I get my money back after moving out?'", "'CIN payslips guarantor'", "'quand récupérer la caution ?'", "'est-ce cher ?'"], "answer": 1,
         "explain": "Exact rare terms are BM25's strength."},
        {"q": "Doc A: rank 1 in BM25, absent from vector results. Doc B: rank 3 in both. With RRF (k=60), who wins?", "options": ["A", "B", "Tie", "Can't tell"], "answer": 1,
         "explain": "A: 1/61 ≈ 0.0164. B: 2/63 ≈ 0.0317."},
    ],
}

DAY21 = {
    "id": "w3d7", "folder": "day21", "retest_task": 2, "date": "2026-10-25", "weekday": "Sun",
    "title": "Retro and your first test set", "minutes": 150,
    "why": "Week 4 measures your RAG. You can't measure without questions whose answers you know.",
    "lesson": r"""
:::hook
Your RAG answered 10 questions this week and they "looked fine". Next week the manager asks: "Is the reranker worth the extra second? Is chunk size 400 better than per-heading?" "Looked fine" can't answer that. A **test set** can: questions with the right answer and the right source, written *before* you look at the system's output.
:::

## What a test item contains

```python
item = {
    "question": "Le propriétaire peut-il augmenter le loyer de 8% ?",
    "lang": "fr",
    "answer": "Non: pas la première année, puis 5% maximum par an.",
    "source_ids": ["c6"],
}
print(item["source_ids"], "-> tests retrieval;", "answer -> tests generation")
```

Two separate checks from one item: **did retrieval find c6?** and **is the answer right?** When something fails, you'll know which half broke.

:::analogy
A test set is a mock exam with the answer key, written by the teacher *before* grading. If the teacher writes the key after reading the student's copy, they'll unconsciously accept the student's answers.
:::

## Ask like a real user

:::predict You copy sentences from the handbook and turn them into questions ("What is the commission of 2% of the final sale price?"). What will your scores look like, and why is that a problem?
---
Excellent, and **misleading**. The question shares exact words with the chunk, so even weak retrieval finds it. Real clients say "how much do I owe you if I buy?", in another language, with typos. Write questions like they do.
:::

:::check
? Why include questions the handbook can't answer?
- To lower the score on purpose
* To check the system says "I don't know" instead of inventing
- Because the check requires it
> A system that always answers looks great on answerable questions and is dangerous in production. Unanswerable items measure honesty.
:::

## The mix that matters

- All three languages, and **cross-language** pairs (French question, Arabic section).
- A few questions that need **two sections** (Sunday visit: visits + opening hours).
- 10-20% **unanswerable**.

:::mistake
Changing the test set after seeing results, to "fix" items the system gets wrong. Freeze it, version it (`questions_v1.json`), and only add new items in a new version.
:::

:::cards
Two things one test item checks? :: Retrieval (source ids) and generation (answer).
Why write questions before looking at outputs? :: So the key isn't biased by the system's answers.
Why unanswerable items? :: To measure if the system admits "I don't know".
Copying handbook sentences as questions? :: Inflates scores: real users paraphrase.
Fixing the test set after results? :: Never. Freeze and version it.
:::

:::explain Explain why a test set needs both the expected answer and the source ids, with one example where they'd tell different stories.
:::
""",
    "files": [
        lab("day21", "questions.json", task=1),
    ],
    "tasks": [
        "Retro: what worked in Week 3, what slipped (2-3 lines in notes)",
        "questions.json: 20 questions, 3 languages, at least 2 unanswerable",
        "Beat the Week 3 boss (8/10)",
        "PFE: one more application ([LinkedIn Jobs](https://www.linkedin.com/jobs/search/?keywords=PFE%20NLP&location=Tunisia))",
    ],
    "done_when": "20 test questions frozen in questions.json, and 8/10 on the boss.",
    "resources": [],
    "quiz": [
        {"q": "A test item's source_ids is used to evaluate...", "options": ["The answer's language", "Retrieval: was the right chunk found?", "Generation speed", "Token cost"], "answer": 1,
         "explain": "Expected answer evaluates generation; source ids evaluate retrieval."},
        {"q": "What share of unanswerable questions is reasonable?", "options": ["0%", "10-20%", "50%", "90%"], "answer": 1,
         "explain": "Enough to measure honesty without dominating the score."},
    ],
    "retest": [
        {"q": "Fixed chunks: size 300, overlap 50. Where does the 4th chunk start?", "options": ["750", "900", "600", "800"], "answer": 0,
         "explain": "Step 250: starts at 0, 250, 500, 750."},
        {"q": "Why keep the heading inside each chunk?", "options": ["Shorter chunks", "It names the topic, helping retrieval", "pgvector needs it", "To avoid overlap"], "answer": 1,
         "explain": "Pieces of a long section may never mention their topic otherwise."},
        {"q": "Documents embedded with bge-m3, questions with e5. Result?", "options": ["Works, both are multilingual", "Similarities are meaningless: two different vector spaces", "Only Arabic breaks", "Slower but correct"], "answer": 1,
         "explain": "Same model for documents and queries, always."},
        {"q": "Normalized rows; scores = matrix @ q. What are the scores?", "options": ["Distances", "Cosine similarities", "Probabilities", "BM25 scores"], "answer": 1,
         "explain": "Unit vectors: dot product = cosine."},
        {"q": "pgvector: which ORDER BY gives the most similar chunks first?", "options": ["ORDER BY embedding <=> q DESC", "ORDER BY embedding <=> q", "ORDER BY 1 - (embedding <=> q)", "ORDER BY embedding <-> q DESC"], "answer": 1,
         "explain": "<=> is a distance: ascending, smallest first."},
        {"q": "Your indexing script is re-run after a crash. What makes this safe?", "options": ["An HNSW index", "INSERT ... ON CONFLICT (id) DO UPDATE", "A bigger batch size", "TRUNCATE before each insert"], "answer": 1,
         "explain": "Upserts make indexing idempotent."},
        {"q": "The answer says 'Yes [5]' and you sent 4 sources. Your code should...", "options": ["Accept it", "Flag it invalid", "Re-send 5 sources", "Drop the citation"], "answer": 1,
         "explain": "A citation to a non-existent source signals hallucination."},
        {"q": "Why must the IDK reply be an exact sentence?", "options": ["Models prefer it", "So code can detect 'not found' reliably", "It's shorter", "It's required by the API"], "answer": 1,
         "explain": "Exact strings are a contract between the prompt and your code."},
        {"q": "Cross-encoder rerankers are used on...", "options": ["All documents", "Only the top candidates from fast retrieval", "Only Arabic text", "The final answer"], "answer": 1,
         "explain": "One model call per pair: affordable only for 10-50 candidates."},
        {"q": "RRF with k=60: doc ranked 2nd in both lists vs doc 1st in one list only. Who wins?", "options": ["The 1st-in-one-list doc", "The 2nd-in-both doc", "Tie", "Depends on BM25 scores"], "answer": 1,
         "explain": "2/62 ≈ 0.032 beats 1/61 ≈ 0.016."},
    ],
}

WEEK3 = {
    "n": 3, "phase": "Phase 1", "title": "RAG from scratch", "dates": "Oct 19-25",
    "goal": "Working RAG over a small document set.",
    "gate": "Working RAG",
    "days": [DAY15, DAY16, DAY17, DAY18, DAY19, DAY20, DAY21],
}
