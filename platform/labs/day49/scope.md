<!-- An example scope page, the agreement that closes week 7. Read it section by section; the panel on the left explains what each part does. -->

# Project scope

## Problem
Agents at a small real estate agency in Sousse answer about 40 repeated client questions a day from memory or by searching 120 PDFs, which takes 5 to 10 minutes for a contract clause. Visits are booked in a paper agenda, and two were double-booked last month.

## User
Four rental agents, 30 to 50 questions a day each, on the office PC and sometimes on a phone.

## In scope
- Answer client questions in Arabic, French, English and Derja from the agency documents, with citations.
- Say "I don't know" when the documents don't answer.
- Book a visit through the visits API, after the agent confirms.

## Out of scope
- Answering clients directly without an agent in the loop.
- Price estimates and market analysis.
- Voice messages and WhatsApp integration.

## Data
The agency rules (PDF, French and Arabic), the fee grid (Word), and about 80 scanned lease contracts with names removed. The manager agreed in writing on 2026-11-20.

## Success metrics
- Answer correct on at least 80% of the golden test set.
- Correct citation on at least 90% of answered questions.
- p95 latency under 10 seconds.
- Cost under 0.005 USD per question.

## Timeline
- Week 8: ingestion, retrieval and citations end to end.
- Week 9: chat, visit booking tool and web UI.
- Week 10: evaluation, two configurations compared.
- Week 11: Docker Compose, tests, CI, README.
- Week 12: demo video and the message to Anis.

## Sign-off
Agreed with the agency manager on 2026-11-22.
