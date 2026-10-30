<!-- An example evaluation report for week 10. Read it section by section; the panel on the left explains what each part does. -->

# Evaluation results

## Setup
Golden test set: 42 questions (18 French, 9 Derja, 8 English, 4 Arabic, 3 Arabizi) across 8 categories, including 6 idk and 4 action items, opened once on 2026-12-12. Three configurations from the grid were compared; answers were judged by an LLM judge whose agreement with my own labels was 0.81 (kappa) on 40 dev answers.

## Results
| config | n | correct | citations | p95 s | USD / query | misses |
|---|---|---|---|---|---|---|
| api-small + hybrid + rerank | 42 | 0.86 [0.74, 0.95] | 0.93 [0.83, 1.00] | 7.4 | 0.0041 | none |
| local qwen2.5:7b + hybrid + rerank | 42 | 0.79 [0.64, 0.90] | 0.90 [0.79, 0.98] | 9.2 | 0.0009 | correct |
| api-small + vector only | 42 | 0.71 [0.57, 0.83] | 0.88 [0.76, 0.98] | 5.1 | 0.0038 | correct, citation_ok |

## Recommendation
api-small + hybrid + rerank. It is the only configuration meeting all four targets, at about 8 USD a month for the agency's volume. The local model is close on accuracy (the intervals overlap) and four times cheaper, but misses the 80% target and runs near the 10 s latency limit on the office PC. I accept sending masked questions to an API; documents and client data stay local.

## Failures
- retrieval_miss: 3 cases, e.g. a Derja question about the plumber's cost where the maintenance chunk was ranked 9th.
- false_idk: 2 cases, e.g. "واش القطط مسموحة؟" answered "I don't know" although the pets chunk was retrieved.
- wrong_answer: 1 case, the seasonal fee read as 10% of one month instead of the whole stay.

## Cost
At 2,000 questions a month: 8.20 USD (25 TND) for the recommended config, 1.80 USD for the local one (electricity only, hardware already there). With hardware bought for the purpose, local becomes cheaper above about 7,500 questions a month.

## Limitations
- 42 test questions give wide intervals (about +/- 10 points); the configs can't be ranked with certainty.
- The judge is an LLM; it disagrees with me on about 1 answer in 10.
- Only one agency's documents: another agency's contracts may behave differently.
