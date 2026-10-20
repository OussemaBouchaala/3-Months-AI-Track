# Your first test set
**Topic:** questions with known answers and known sources: the ruler you'll measure RAG with all of Week 4.

## Real example
A bank tests its FAQ bot with a spreadsheet of questions, the right answer, and where it's written. Each row lets you check two things separately: did retrieval find the source, and is the answer right?

```python
tests = [
    {"question": "What's the daily ATM limit?", "lang": "en", "answer": "1,000 TND", "source_ids": ["atm-2"]},
    {"question": "Quel est le plafond du virement en ligne ?", "lang": "fr", "answer": "5 000 TND par jour", "source_ids": ["web-4"]},
    {"question": "هل يمكن فتح حساب بالدولار؟", "lang": "ar", "answer": "", "source_ids": []},   # not in the docs
]
retrieved = {"What's the daily ATM limit?": ["atm-2", "atm-1"]}
for t in tests[:1]:
    print(t["question"], "-> source found:", set(t["source_ids"]) <= set(retrieved[t["question"]]))
```

## Your mission
Write 20 questions about the handbook, with the expected answer and the chunk ids that contain it.

## Steps
1. Open `../day15/chunks.json` to see which id (c0 to c13) holds which section.
2. At least 4 questions per language (`"en"`, `"fr"`, `"ar"`). Ask some in a different language than the section they target: that's the hard part.
3. At least 2 questions the handbook can't answer: empty `answer`, `source_ids: []`.
4. Ask the way a real client would ("can I bring my cat?"), not by copying sentences.

## Done when
**Check** confirms 20 valid questions, all three languages, and unanswerable ones.
