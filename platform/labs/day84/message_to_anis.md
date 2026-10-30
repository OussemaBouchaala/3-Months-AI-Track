<!-- An example of the message that closes the program. Read it section by section; the panel on the left explains what each part does. -->

Subject: Accuracy, latency and cost of the agency assistant

Hi Anis,

When we spoke in October, you told me a project is only convincing with three numbers: accuracy, latency and cost. I spent the last six weeks building one and measuring exactly that.

It's a document assistant for a real estate agency in Sousse: agents paste a client's question in Arabic, French or Derja and get the answer from the agency's documents with the source, and it can book a visit after the agent confirms.

On 42 held-out questions it answers correctly 86% of the time (confidence interval 74 to 95%), with a p95 latency of 7.4 s, for about 25 TND a month at the agency's volume. A local 7B model reaches 79% for almost nothing, which I document as the cheaper option. Its main limitation is still questions written in Arabizi.

Code and full evaluation: https://github.com/OussemaBouchaala/dar-assistant
Four-minute demo: https://youtu.be/demo-video-id

Would you have 20 minutes in early January to give me your feedback on the evaluation, and tell me what you would expect from a junior AI engineer on your team?

Best regards,
Oussema
