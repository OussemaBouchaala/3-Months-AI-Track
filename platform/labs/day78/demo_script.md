<!-- An example 3-5 minute demo script. Read it section by section; the panel on the left explains what each part does. -->

# Demo script (3-5 minutes)

## Scene 1 - Hook (0:20)
Rental agents at a Sousse agency answer about 40 repeated client questions a day, often by digging through scanned contracts. I built an assistant that answers them in seconds, with the source.
Screen: the agency's WhatsApp with a pile of client questions.

## Scene 2 - Live question in Derja (0:45)
A client writes in Derja: "شنوة الضمان كي نكري دار؟". I paste it as is. The answer comes back in Derja in four seconds: two months of rent, with source [1], the agency rules, article on deposits.
Screen: the web page, the answer streaming in, the source line under it.

## Scene 3 - Follow-up (0:30)
The client continues: "et avec un chat ?". The assistant keeps the context and answers two and a half months, citing both the deposit rule and the pets rule.
Screen: the follow-up and the two citations [1] and [2].

## Scene 4 - Booking with confirmation (0:40)
Now: "Réserver une visite du L12 samedi à 10h pour Amel". Nothing is booked yet. The assistant shows the exact date and time and waits. I click Confirmer once; clicking again doesn't book twice.
Screen: the preview sentence, the Confirmer button, then the visit in the agency's visits list.

## Scene 5 - Honest I don't know (0:25)
A question the documents don't cover: "Quel est le prix du m2 à Sahloul ?". It says it doesn't know based on the documents, instead of inventing a price.
Screen: the "I don't know based on the documents" answer with no source.

## Scene 6 - The numbers (0:40)
On 42 held-out questions in five languages, it answers correctly 0.86 [0.74, 0.95], cites the right source 93% of the time, with a p95 latency of 7.4 seconds and about 25 TND a month. The main remaining failure is retrieval on Derja questions.
Screen: the results table from the README.

## Scene 7 - How it runs (0:25)
It runs on the agency's own PC with one command, docker compose up. Phone numbers and IDs are masked before anything is indexed, logged or sent to an API.
Screen: the terminal with docker compose ps, all services healthy.

## Scene 8 - Close (0:20)
Next I'd improve Arabizi handling, the weakest category. I'm Oussema; the code, the evaluation and this demo are linked below.
Screen: the GitHub repository page with the green CI badge.
