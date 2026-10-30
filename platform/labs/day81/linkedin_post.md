<!-- An example LinkedIn post to publish with the demo video. Read it section by section; the panel on the left explains what each part does. -->

Rental agents at a real estate agency in Sousse answer about 40 identical client questions a day. I spent 6 weeks building them an assistant.

They paste a client's WhatsApp message, in Arabic, French, English or Derja, and get the answer from the agency's own documents in a few seconds, with the exact contract article it comes from. It can also book a visit, but only after the agent confirms.

On 42 held-out questions it answers correctly 86% of the time, cites the right source 93% of the time, responds in under 7.4 seconds for 95% of questions, and costs about 25 TND a month to run.

What surprised me: the biggest gain didn't come from a better model. It came from normalizing Arabic spelling (أ, إ and ا are three different letters to a computer), which added 11 points of retrieval accuracy. What still fails: questions written in Arabizi, like "9adeh el kra", which is next on my list.

Everything runs on the agency's PC with one Docker command, and phone numbers and ID numbers are masked before anything is stored or sent to an API.

Code, evaluation and the 4-minute demo: https://github.com/OussemaBouchaala/dar-assistant

#RAG #NLP #Arabic #MachineLearning #Tunisia
