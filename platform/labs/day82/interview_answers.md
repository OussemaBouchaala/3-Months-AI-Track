<!-- Example answers to five questions asked in every AI engineering interview. Read it section by section; the panel on the left explains what each part does. -->

# Interview answers

## Q1: Tell me about a project you're proud of.
A real estate agency in Sousse gets about 40 repeated client questions a day, in Arabic, French and Derja, and the answers are buried in 120 documents, many of them scanned contracts. I built them an assistant over six weeks. I interviewed an agent first to collect real questions, then built the pipeline: parsing and OCR, Arabic normalization, hybrid search with reranking, answers with checked citations, and a visit-booking tool that only runs after the agent confirms. I deployed it on their office PC with Docker Compose and CI. On 42 held-out questions it answers correctly 86% of the time, with a p95 latency of 7.4 seconds and a cost of about 25 TND a month. What I'm proudest of is that the agents actually used it in a usability test and found problems I had never seen, which I fixed the same weekend.

## Q2: What was the hardest technical problem, and how did you solve it?
Retrieval on Arabic text. At first, keyword search missed obvious matches because the same word is spelled several ways: different alef forms, taa marbuta written as haa, diacritics, and articles glued to words like "والمدرسة". I measured it before fixing anything: recall at 5 was 0.61 on 100 ARCD questions. I then added one change at a time and measured each: normalization, then light stemming with a minimum stem length so short words aren't destroyed, then hybrid search with reciprocal rank fusion. Normalization alone gave 11 points; hybrid search another 7. I learned to treat each idea as an experiment with a number, instead of stacking changes and hoping.

## Q3: How did you know your system worked? How did you evaluate it?
I built a golden set from the agent's own questions, word for word, plus variations in other languages, questions the documents can't answer, and booking requests. I split it once into dev and test, stratified by category, and only opened the 42-question test set at the end. I used an LLM judge, but first checked its agreement with my own labels on 40 answers: kappa 0.81. I reported accuracy with bootstrap confidence intervals, 0.86 with an interval from 0.74 to 0.95, and used a paired bootstrap to compare configurations, because with 42 questions a 4-point difference can be noise. I also classified every failure by cause, which showed retrieval misses on Derja were the top problem.

## Q4: Tell me about something that failed, and what you learned.
My first booking flow looked fine in my own tests, but in the usability test 2 of 4 agents read the confirmation preview, said "OK, it's done", and moved on. The visit was never booked, because the Confirm button was below a long answer. I had tested that the code worked, not that people understood it. I moved the button above the details and changed the message to start with "To confirm:", and the next agent got it right first time. Since then I watch at least 3 real users before calling a feature finished, and I learned that a passing test suite says nothing about whether the interface is clear.

## Q5: Why did you choose this design over the alternatives?
For generation I recommended a small API model instead of the local 7B model, although local was my first choice for privacy. The local model scored 0.79 against 0.86, and its p95 latency was 9.2 seconds on the office PC, close to the 10-second target the agent gave me. The trade-off is that questions leave the building, so I mask phone numbers, ID numbers and names before any API call, and documents and the index stay local. The cost is about 25 TND a month instead of almost nothing in electricity. I documented the break-even: above about 7,500 questions a month, buying a GPU becomes cheaper than the API.

## Questions I'll ask them
- How do you evaluate a model change before it reaches users?
- What does the data look like for the team I'd join, and who labels it?
- What would a successful first three months look like in this role?
