<!-- An example Phase 1 report, with realistic numbers. Read how each section is built: a results table where each row adds one change, claims tied to numbers, honest failures. -->

# Phase 1 report: Arabic RAG prototype

## Summary
In Phase 1 I built a retrieval-augmented question answering pipeline, first on a trilingual agency handbook and then on ARCD, a real Arabic reading-comprehension dataset. The best configuration (normalization, hybrid search and reranking) finds the right document in the top 5 for 0.84 of the questions. The biggest single gain came from Arabic normalization, not from a bigger model.

## Corpus
- ARCD (Arabic Reading Comprehension Dataset), Modern Standard Arabic, Wikipedia paragraphs.
- 1,395 questions over 465 unique paragraphs after deduplication by exact context text.
- I evaluated on a fixed random sample of 100 questions (seed 0).

## Pipeline
- Normalization: diacritics, tatweel, alef variants, taa marbuta, Arabic-Indic digits.
- Chunking: sentence-aware chunks of 500 characters with 1 sentence of overlap.
- Embeddings: bge-m3 through Ollama, stored in pgvector.
- Search: hybrid, vector plus BM25 on light-stemmed tokens, fused with RRF.
- Reranking: top 20 reranked, top 5 kept.
- Answer: the LLM answers from the chunks only, or says it doesn't know.

## Results
| config | recall@5 | answer found |
|---|---|---|
| baseline (raw text, vector only) | 0.61 | 38% |
| + normalization | 0.72 | 45% |
| + hybrid BM25 | 0.79 | 49% |
| + rerank | 0.84 | 53% |

## What worked
- Normalization added 11 points of recall@5 on its own, because questions and paragraphs spell alef and taa marbuta differently.
- Hybrid search helped most on names and dates, where keyword matching beats embeddings (+7 points).

## What didn't
- Answer found stays near 50%: the LLM often paraphrases the gold span, so exact matching undercounts correct answers.
- Questions with Arabizi or dialect words, for example "9adeh el kra", retrieve almost nothing useful.

## Next
Phase 2 keeps the normalization, the sentence chunker, hybrid search and the evaluation harness as they are. It changes the answer metric to an LLM judge checked against my own labels, and adds dialect handling for the client's real messages.
