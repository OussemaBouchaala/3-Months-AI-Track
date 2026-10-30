<!-- An example usability report after testing the chat page with real users. Read it section by section; the panel on the left explains what each part does. -->

# Usability test report

## Participants
4 agents from the agency (3 rental agents, 1 sales agent). All use WhatsApp on their phones and the office PC; they write French and Derja, read Arabic.

## Tasks
1. A client asks in Derja how much the deposit is. Find the answer and its source.
2. Book a visit of L12 for Saturday 10:00 for a client.
3. Find which contract clause says pets increase the deposit.

## Results
| task | n | success | median s | errors |
|---|---|---|---|---|
| deposit question | 4 | 100% | 34 | 1 |
| book a visit | 4 | 75% | 88 | 4 |
| pet clause | 4 | 50% | 120 | 3 |

Mean SUS score: 71.9, grade C (slightly above average).

## Issues
- [high] The Confirm button was missed by 2/4 users: it appears under a long answer and they thought the visit was booked.
- [high] Sources show doc ids like "bail_043" instead of a readable title: 3/4 users could not tell which contract it was.
- [medium] Arabic answers are left-aligned on the PC when the question was French: 2/4 users.
- [low] Enter sends the message; one user wanted a new line.

## Changes made
- The confirm message now starts with "À confirmer :" in bold and the button is shown before the details.
- Sources show the document title and article, with the doc id in small text.
- Each message sets dir="auto" separately, so mixed conversations align correctly.

## Next
Week 10 will measure citation accuracy per document type (contracts vs rules), since the pet clause task failed on scanned contracts, and the share of action requests that reach a confirm step.
