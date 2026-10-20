"""Week 6: Real Arabic data (Nov 9-15, 2026)."""
from lab_files import lab

DAY36 = {
    "id": "w6d1", "folder": "day36", "date": "2026-11-09", "weekday": "Mon",
    "title": "A real Arabic corpus", "minutes": 75,
    "why": "The handbook was written for the course. Real data is messier, bigger, and in the language your client actually uses.",
    "lesson": r"""
:::hook
Your RAG scored well on 14 hand-written sections. A client in Sfax will send you 3,000 Arabic PDFs, half-scanned, with three spellings of the same word. Before that day, you want to have hit those problems on a public dataset, where nobody is waiting for you.
:::

## ARCD: questions with their source

**ARCD** (Arabic Reading Comprehension Dataset) has about 1,400 questions written by people about Arabic Wikipedia paragraphs. Each row holds:
- `context`: the paragraph,
- `question`,
- `answers`: the answer span copied from the paragraph.

That's a free test set: for each question you already know the right document **and** the answer.

:::analogy
Week 4 you wrote your own exam questions. ARCD is a past exam with the answer key stapled to it. You still have to check that the key is fair, but you don't have to write 1,000 questions.
:::

## Many questions, one paragraph

Several questions point to the same paragraph. If you index each row's context, the same paragraph is stored five times, and your top 5 results are five copies of one text.

```python
rows = [{"context": "Sousse is a city...", "question": "Where is Sousse?"},
        {"context": "Sousse is a city...", "question": "How old is Sousse?"},
        {"context": "Kairouan is...", "question": "What is Kairouan known for?"}]
doc_ids = {}
for r in rows:
    doc_ids.setdefault(r["context"], f"d{len(doc_ids)}")
print(doc_ids)
print([(r["question"], doc_ids[r["context"]]) for r in rows])
```

:::predict You forgot to deduplicate and index all 1,400 contexts. Your recall@5 at document level looks... better or worse than reality?
---
It's distorted. Duplicates fill the top 5 with the same paragraph, so other relevant documents get pushed out, and the counts of "documents" are wrong. Deduplicate first, keep the question → doc_id link.
:::

## Getting the rows without a big download

The Hugging Face **datasets-server** gives rows as JSON pages: `/rows?dataset=...&config=...&split=...&offset=0&length=100`. Page through with the offset until you have them all. No library, just HTTP.

:::check
? Why save the corpus as JSONL (one JSON object per line)?
- It's smaller than CSV
* You can append, stream and read it line by line, and Arabic text stays intact with ensure_ascii=False
- Pandas can't read JSON
- It encrypts the data
> JSONL is the default format for text datasets. Always open files with encoding="utf-8".
:::

:::mistake
`json.dumps(row)` without `ensure_ascii=False`. Your Arabic becomes `ال...` in the file. It still loads, but you can't read or grep it any more.
:::

:::cards
What does ARCD give per row? :: A paragraph, a question, and the answer span.
Why deduplicate contexts? :: Many questions share one paragraph; duplicates pollute the top k.
What links a question to its document? :: The doc_id from the context dictionary.
How do you page through datasets-server? :: offset and length parameters, 100 rows per call.
Saving Arabic to JSON? :: ensure_ascii=False and encoding="utf-8".
:::

:::explain Explain to a classmate why a dataset with questions and answer spans saves you a week of work.
:::
""",
    "files": [
        lab("day36", "load_corpus.py", task=[0, 1]),
    ],
    "tasks": [
        "load_corpus.py: page through the datasets-server rows API",
        "Deduplicate paragraphs, save docs and questions as JSONL",
        "Skim 10 paragraphs and 10 questions: note what looks hard",
    ],
    "done_when": "arcd_docs.jsonl and arcd_questions.jsonl on disk, every question pointing to a doc id.",
    "resources": [{"label": "ARCD on Hugging Face", "url": "https://huggingface.co/datasets/hsseinmz/arcd"},
                  {"label": "datasets-server: /rows", "url": "https://huggingface.co/docs/dataset-viewer/rows"}],
    "quiz": [
        {"q": "Five ARCD questions share one paragraph. How many documents do you index?", "options": ["5", "1", "0", "It depends on the model"], "answer": 1,
         "explain": "Deduplicate by context; the questions keep a pointer to it."},
        {"q": "Your saved file shows \\u0627\\u0644... instead of Arabic. Cause?", "options": ["Wrong dataset", "json.dumps without ensure_ascii=False", "The model", "A bad offset"], "answer": 1,
         "explain": "The default escapes non-ASCII characters."},
    ],
}

DAY37 = {
    "id": "w6d2", "folder": "day37", "notes_task": 2, "date": "2026-11-10", "weekday": "Tue",
    "title": "Normalizing Arabic", "minutes": 75,
    "why": "The same word can be typed five ways in Arabic. If the query and the document disagree, keyword search finds nothing.",
    "lesson": r"""
:::hook
A user types `اسعار`. The document says `أسعار`. To a computer these are two different strings, so BM25 scores zero. Same for `مدرسة` vs `مدرسه`, and `٢٠٢٥` vs `2025`. One small function fixes most of this.
:::

## What varies, and what to do

| Variation | Example | Normalize to |
|---|---|---|
| Diacritics (harakat) | مَدْرَسَة | مدرسة |
| Tatweel (stretching) | مـــدرسة | مدرسة |
| Alef forms | أ إ آ | ا |
| Taa marbuta | ة | ه |
| Alef maqsura | ى | ي |
| Arabic-Indic digits | ٢٠٢٥ | 2025 |

```python
import re
DIAC = re.compile("[ً-ْٰ]")
def norm(t):
    t = DIAC.sub("", t).replace("ـ", "")
    t = re.sub("[أإآ]", "ا", t).replace("ة", "ه").replace("ى", "ي")
    return t.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))
print(norm("مَدْرَسَة"), norm("مـــدرسة"), norm("أسعار") == norm("اسعار"), norm("٢٠٢٥"))
```

:::analogy
Lowercasing English: "Price", "PRICE" and "price" are the same word for search. Arabic normalization is the same move, with more cases.
:::

## Apply it on both sides

Normalize the **documents** at index time and the **query** at search time, with the same function. Keep the original text for display: users should see `مَدْرَسَة` if that's what the source says.

:::predict You normalize the documents but forget the query. What happens to "أسعار الكراء"?
---
The query keeps `أ`, the index only has `ا`: no keyword match. Same function, both sides, always.
:::

## Embeddings care less, but not zero

bge-m3 saw a lot of messy Arabic and mostly maps variants close together. Normalization matters most for **keyword** search. Measure both on Saturday instead of guessing.

:::check
? Why keep the original text next to the normalized one?
- Normalized text is longer
* To show users the source as written, and quote it exactly
- Embeddings need diacritics
- JSONL requires it
> Normalize for matching, show the original.
:::

:::mistake
Over-normalizing: turning every `ي` and `ى` and `ه` and `ة` into one form can merge different words. Keep the rules few, test them on real pairs, and make risky rules (like taa marbuta) a switch.
:::

:::cards
Harakat? :: Short-vowel diacritics; usually stripped for search.
Tatweel? :: The stretching character ـ; always removed.
أ إ آ → ? :: ا
Where to normalize? :: Documents at index time AND the query at search time.
What to display? :: The original text.
:::

:::explain Explain to a French-speaking developer why "أسعار" and "اسعار" don't match, and the fix.
:::
""",
    "files": [
        lab("day37", "arabic_norm.py", task=[0, 1]),
    ],
    "tasks": [
        "arabic_norm.py: diacritics, tatweel, alef, letters, digits",
        "Normalize the ARCD docs and questions; count how many changed",
        "Note 3 normalizations you'd be careful with",
    ],
    "done_when": "normalize_arabic passes the checks and you know how many ARCD questions change.",
    "resources": [{"label": "Arabic diacritics (Wikipedia)", "url": "https://en.wikipedia.org/wiki/Arabic_diacritics"}],
    "quiz": [
        {"q": "Where should Arabic normalization be applied?", "options": ["Only documents", "Only the query", "Both, with the same function", "Only the LLM answer"], "answer": 2,
         "explain": "Otherwise the two sides still disagree."},
        {"q": "Which search suffers most from unnormalized spelling?", "options": ["Keyword / BM25", "Embeddings", "Both equally", "Neither"], "answer": 0,
         "explain": "Exact token matching; embeddings are more forgiving."},
    ],
}

DAY38 = {
    "id": "w6d3", "folder": "day38", "date": "2026-11-11", "weekday": "Wed",
    "title": "Arabic keyword search", "minutes": 75,
    "why": "Arabic glues articles and pronouns onto words. Without light stemming, BM25 sees والمدرسة and مدرسة as strangers.",
    "lesson": r"""
:::hook
`والمدرسة` means "and the school". It's one token. Your query is `مدرسة`. BM25 compares whole tokens, so: zero. In English that would be like "andtheschool" vs "school".
:::

## Light stemming: peel prefixes and suffixes

Not a full morphological analysis (that's heavy and slow). Just:
- **Prefixes**: و (and), ف (so), ب (with), ل (for), ك (like), ال (the), and their combinations: وال، بال، لل...
- **Suffixes**: pronouns and plurals: ها، هم، ات، ون، ين...
- **A minimum stem length**, so short words don't get eaten.

```python
PRE = ["وال", "بال", "ال", "و", "ب", "ل"]
def stem(w):
    for p in PRE:
        if w.startswith(p) and len(w) - len(p) >= 3:
            return w[len(p):]
    return w
print([stem(w) for w in ["والمدرسة", "بالبيت", "المكتب", "ولد"]])
```

:::analogy
Taking off coat, scarf and hat before getting on the scale. You only remove what's clearly clothing, not an arm.
:::

## The minimum length rule

`ولد` (boy) starts with `و`, but it's part of the word. Strip it and you get `لد`, which matches nonsense. The `len >= 3` rule keeps it. Single-letter suffixes like `ه` and `ي` are even riskier: `مدرسه` (normalized) would lose its last letter. Leave them out.

:::predict You add a stemmer and recall@5 goes **down** on names (people, cities). Why?
---
Names get stemmed too: `بنزرت` or `الكاف` lose letters and match other words. Stemming trades precision for recall. That's why you measure, and why hybrid search keeps embeddings in the mix.
:::

:::check
? What does the stemmer need to be used with?
- A bigger embedding model
* The same normalization and stemming on documents and query
- A GPU
- Diacritics kept on
> Same pipeline on both sides, again.
:::

:::mistake
Stemming the text you show users or send to the LLM. Stems are for matching only: the LLM should read the real sentence.
:::

:::cards
والمدرسة → ? :: مدرسه (after normalization and stripping وال)
Why a minimum stem length? :: Short words would lose real letters (ولد).
Light vs full stemming? :: Light peels affixes; full analyzes roots and patterns.
What gets stemmed? :: Tokens for keyword matching, never the displayed text.
Stemming risk? :: Names and short words get over-matched.
:::

:::explain Explain light stemming with one Arabic example and one English equivalent.
:::
""",
    "files": [
        lab("day38", "arabic_keywords.py", task=[0, 1]),
    ],
    "tasks": [
        "arabic_keywords.py: light_stem with prefixes, suffixes, minimum length",
        "tokenize_ar and overlap; plug it into Week 3's BM25",
        "Try 10 ARCD questions: list 2 where stemming hurt",
    ],
    "done_when": "Keyword overlap finds والمدرسة for the query مدرسة, and ولد stays ولد.",
    "resources": [{"label": "Larkey et al., light stemming for Arabic IR", "url": "https://ciir.cs.umass.edu/pubfiles/ir-249.pdf"}],
    "quiz": [
        {"q": "Why does والمدرسة not match مدرسة in plain BM25?", "options": ["Encoding", "Prefixes glued to the word make it a different token", "Diacritics", "Right-to-left text"], "answer": 1,
         "explain": "و + ال + مدرسة is one token."},
        {"q": "Why keep a minimum stem length?", "options": ["Speed", "To avoid stripping real letters from short words", "Memory", "The API needs it"], "answer": 1,
         "explain": "ولد would become لد."},
    ],
}

DAY39 = {
    "id": "w6d4", "folder": "day39", "notes_task": 2, "date": "2026-11-12", "weekday": "Thu",
    "title": "Mixed text and Arabizi", "minutes": 75,
    "why": "Tunisian clients write Arabic, French, English and Arabizi in one message. Your pipeline has to know which is which.",
    "lesson": r"""
:::hook
Real message from a client: `salam, 9adeh el kra mta3 S+2 à Sahloul? merci`. Arabic words in Latin letters with digits (Arabizi), French, and a property code. Your Arabic normalizer does nothing to it. Your French tokenizer thinks `9adeh` is noise.
:::

## Script first, language second

Look at characters:
- Arabic block (U+0600 to U+06FF) → Arabic script.
- Latin letters → French, English **or Arabizi**.
- Digits inside a Latin word (`3`, `7`, `9`, `5`) → probably Arabizi: `3` = ع, `7` = ح, `9` = ق.

```python
import re
def script(tok):
    if re.search("[؀-ۿ]", tok): return "ar"
    if re.search("[A-Za-z]", tok): return "latin"
    return "other"
msg = "salam 9adeh el kra à Sahloul مرحبا 2025"
print([(t, script(t)) for t in msg.split()])
print([t for t in msg.split() if re.fullmatch(r"[a-z]*[23579][a-z0-9]*", t) and re.search("[a-z]", t)])
```

:::analogy
Sorting mail by the alphabet on the envelope before reading it. You don't read a Japanese letter with a French dictionary.
:::

## Rules beat models here (for now)

A tiny rule set (script ratio, a few French and English stop words, Arabizi digit patterns) gets most messages right and is explainable. A language-ID model is better on long text but weak on 6-word chat messages full of code-switching.

:::predict "Le prix est 3 mille" contains the digit 3. Is it Arabizi?
---
No. `3` is a separate token, not inside a word. Arabizi digits sit **inside** Latin words (`3andek`, `9adeh`). And the French stop words (le, est) outnumber Arabizi hits. That's why the rule compares counts.
:::

## What to do with each

- Arabic: normalize, stem, search.
- French/English: lowercase, search.
- Arabizi: hardest. Embeddings partly cope; for keywords you'd need transliteration. On Day 39 you only **detect** it, so you can count how often it happens and decide later.

:::check
? Why split a mixed message into runs of the same script?
- To translate it
* So each run gets the processing for its own script
- To count characters
- Because the LLM needs it
> Arabic normalization on French text is useless; French lowercasing on Arabic does nothing. Route each run.
:::

:::mistake
Treating every digit as Arabizi. Prices, dates and codes like S+2 are full of digits. Only digits glued to Latin letters count.
:::

:::cards
Arabizi? :: Arabic (often dialect) written in Latin letters with digits for missing sounds.
3, 7, 9 in Arabizi? :: ع, ح, ق
First thing to detect? :: The script of each token (Arabic block vs Latin).
Why rules first? :: Short code-switched messages fool language-ID models; rules are explainable.
What do you do with Arabizi this week? :: Detect and count it; handle it later.
:::

:::explain Explain to the agency manager why their clients' WhatsApp messages are harder for search than their PDFs.
:::
""",
    "files": [
        lab("day39", "mixed_text.py", task=[0, 1]),
    ],
    "tasks": [
        "mixed_text.py: script_of, script_ratio, is_arabizi",
        "detect_lang and split_runs on mixed messages",
        "Write 5 messages the way your Tunisian clients would; note which ones the rules get wrong",
    ],
    "done_when": "Five mixed messages labeled correctly, including one Arabizi.",
    "resources": [{"label": "Arabic chat alphabet (Arabizi)", "url": "https://en.wikipedia.org/wiki/Arabic_chat_alphabet"}],
    "quiz": [
        {"q": "Which token is most likely Arabizi?", "options": ["2025", "S+2", "3andek", "prix"], "answer": 2,
         "explain": "A digit inside a Latin word, standing for ع."},
        {"q": "First step on a mixed message?", "options": ["Translate it", "Detect the script of each token or run", "Embed it", "Remove digits"], "answer": 1,
         "explain": "Then route each run to the right processing."},
    ],
}

DAY40 = {
    "id": "w6d5", "folder": "day40", "date": "2026-11-13", "weekday": "Fri",
    "title": "Chunking Arabic text", "minutes": 75,
    "why": "Character chunks cut Arabic sentences in half. Sentence-aware chunks keep meaning together and make better citations.",
    "lesson": r"""
:::hook
Your Week 3 chunker cuts every 500 characters. On Arabic Wikipedia it splits `...تأسست المدينة سنة` | `814 م على يد...`. The year is in one chunk, the fact it belongs to is in another. A question about the founding date retrieves half an answer.
:::

## Arabic punctuation

Arabic uses its own marks: `؟` (question mark), `؛` (semicolon), `،` (comma). A splitter that only knows `. ! ?` never sees the end of an Arabic question.

```python
import re
text = "ما هي عاصمة تونس؟ العاصمة هي تونس. وهي أكبر مدينة؛ يسكنها أكثر من مليون."
print(re.split(r"(?<=[.!?؟؛])\s+", text))
```

:::analogy
Cutting a cake: you cut between the layers, not through the decoration. Sentences are the layers.
:::

## Pack sentences, overlap by sentences

1. Split into sentences.
2. Add sentences to the current chunk until the next one would pass `max_chars`.
3. Start the next chunk with the last sentence of the previous one (overlap = 1 sentence).
4. Chunk ids `d12-c0`, `d12-c1`: the document is everything before `-c`.

:::predict One sentence is 900 characters, and max_chars is 500. What should the chunker do?
---
Keep it as its own chunk, longer than the limit. Cutting it in the middle is exactly what we're avoiding; a slightly long chunk is fine. (The alternative is a fallback split on `،`.)
:::

## Keep the document id in the chunk id

On Saturday you'll measure recall at **document** level: "did any chunk of the right paragraph come back?" That only works if every chunk knows its document. `doc_of("d12-c3")` → `d12`.

:::check
? Why overlap by whole sentences rather than by 50 characters?
- It's faster
* A sentence is a unit of meaning; 50 characters can be half a word
- Embeddings require it
- It uses less memory
> Overlap exists to keep context across a boundary; half-words don't carry any.
:::

:::mistake
Splitting on `.` inside numbers and abbreviations: `3.5` or `م.` (for "year"). The regex needs a space after the mark, which avoids the number case.
:::

:::cards
Arabic question mark? :: ؟
Arabic semicolon? :: ؛
Overlap unit in a sentence chunker? :: Whole sentences, usually 1.
A sentence longer than max_chars? :: Keep it whole as its own chunk.
doc_of("d12-c3")? :: d12
:::

:::explain Explain why a citation from a sentence-aware chunk is more useful to a user than one from a fixed-size chunk.
:::
""",
    "files": [
        lab("day40", "arabic_index.py", task=[0, 1]),
    ],
    "tasks": [
        "arabic_index.py: split_sentences with Arabic punctuation, chunk_sentences with overlap",
        "build_chunks over ARCD and embed them with bge-m3",
        "Compare chunk counts and average length with Week 3's character chunker",
    ],
    "done_when": "arcd_chunks.json and arcd_embeddings.npy on disk; no chunk starts mid-sentence.",
    "resources": [],
    "quiz": [
        {"q": "Which character ends an Arabic question?", "options": ["?", "؟", "،", "؛"], "answer": 1,
         "explain": "The reversed question mark."},
        {"q": "Why put the document id in the chunk id?", "options": ["Sorting", "To measure recall and cite at document level", "Compression", "The database needs it"], "answer": 1,
         "explain": "doc_of maps a retrieved chunk back to its source."},
    ],
}

DAY41 = {
    "id": "w6d6", "folder": "day41", "date": "2026-11-14", "weekday": "Sat",
    "title": "Evaluate on Arabic", "minutes": 180,
    "why": "Every choice this week (normalize, stem, chunk) was a guess until you measure it on real questions.",
    "lesson": r"""
:::hook
You added normalization, stemming and a new chunker this week. Did each one help? Or did stemming hurt names while normalization helped dates? Without a table, you'll defend your choices with feelings. Today you get the table.
:::

## One change per row

| variant | what changes |
|---|---|
| vector | bge-m3 on the raw chunks |
| BM25 raw | whitespace tokens |
| BM25 normalized + stemmed | day37 + day38 |
| hybrid (RRF) | vector + BM25 normalized |

Each row differs from another by **one** thing, so each difference has a cause. Add a `Δ` column against the baseline so the reader doesn't do subtraction.

:::analogy
A cooking test: change only the salt, taste; then only the time, taste. Change both and you don't know which one fixed the dish.
:::

## Document-level recall

Retrieval returns chunks; ARCD's truth is the paragraph. Map chunks to documents (first appearance, no duplicates), then compute Week 4's recall@k.

```python
chunks = ["d3-c0", "d7-c2", "d3-c1", "d9-c0"]
docs = []
for c in chunks:
    d = c.rsplit("-c", 1)[0]
    if d not in docs: docs.append(d)
print(docs, "recall@2 for d7:", float("d7" in docs[:2]))
```

## Answer found: cheap but strict

ARCD answers are spans from the paragraph. "Is the normalized gold span inside the normalized prediction?" is a cheap answer metric. It undercounts paraphrases (the LLM says "814 AD", gold is "سنة 814"), so read 10 misses before trusting it.

:::predict 100 questions, recall@5 goes from 0.70 to 0.73. Is the change real?
---
Not sure. 3 questions out of 100 can be noise. Look at which questions flipped, and in Week 10 you'll compute a confidence interval. For now: report it, don't celebrate it.
:::

:::check
? Why a fixed random seed for the 100-question sample?
- It's faster
* So every run compares the variants on the same questions
- The API needs it
- To get better scores
> Different samples would mix "variant changed" with "questions changed".
:::

:::mistake
Tuning on the 100 questions and reporting on the same 100. That's grading your own homework with the answers open. Keep a second sample untouched for the final number.
:::

:::cards
One row of an ablation table changes...? :: One thing.
Δ column? :: Difference vs the baseline, so readers see the gain directly.
Document-level recall? :: Map chunks to documents, then recall@k.
Answer-found weakness? :: Undercounts correct paraphrases.
Same questions every run? :: Fixed seed.
:::

:::explain Explain to the agency manager what "recall@5 = 0.8" means, without the word "recall".
:::
""",
    "files": [
        lab("day41", "arabic_eval.py", task=[0, 1]),
    ],
    "tasks": [
        "arabic_eval.py: sample, document ranking, recall, answer found, comparison table",
        "Run the 4 variants on 100 ARCD questions, save arabic_results.md",
        "Read 10 misses of the best variant and label why each failed",
    ],
    "done_when": "arabic_results.md has 4 rows with a Δ column, and you can say which change helped most.",
    "resources": [],
    "quiz": [
        {"q": "Why does an ablation table change one thing per row?", "options": ["Shorter table", "So each difference has a clear cause", "Faster runs", "Tradition"], "answer": 1,
         "explain": "Two changes at once can't be separated."},
        {"q": "Chunks d3-c0, d3-c1, d7-c0. Documents in order?", "options": ["d3, d3, d7", "d3, d7", "d7, d3", "d0, d1"], "answer": 1,
         "explain": "First appearance, no duplicates."},
    ],
}

DAY42 = {
    "id": "w6d7", "folder": "day42", "retest_task": 1, "date": "2026-11-15", "weekday": "Sun",
    "title": "Phase 1 report", "minutes": 150,
    "why": "Phase 1 ends here. One honest page of numbers is what you'll show Anis, and what you'll reuse in Phase 2.",
    "lesson": r"""
:::hook
Six weeks ago you had never embedded a sentence. Now you have a hybrid Arabic RAG with an evaluation harness. If someone asks "how good is it?", you should answer in one sentence with one number, then show a table. Today you write that page.
:::

## The shape of the Phase 1 report

1. **Summary**: what, on which data, the key number.
2. **Corpus**: dataset, counts, deduplication.
3. **Pipeline**: one bullet per stage.
4. **Results**: the table, one change per row.
5. **What worked / what didn't**: each tied to a number or an example.
6. **Next**: what Phase 2 keeps and changes.

:::analogy
The end-of-season report of a coach: record, stats per player, what the training changed, what to work on next season. Not "we played with heart".
:::

## Numbers that travel

A number is only useful with its context: `recall@5 = 0.84 on 100 ARCD questions (seed 0), document level`. Without the "on what", nobody can compare it to anything.

```python
rows = [("baseline", 0.61), ("+ normalization", 0.72), ("+ hybrid", 0.79), ("+ rerank", 0.84)]
base = rows[0][1]
for name, r in rows:
    print(f"| {name} | {r:.2f} | {r - base:+.2f} |")
```

:::predict Your best variant improves recall@5 by 0.23 but doubles the latency. Does the report mention latency?
---
Yes. A reader deciding to ship needs both. If you measured it in Week 4 (stage_timer), put it in a column. If you didn't, say so in "What didn't".
:::

:::check
? Which "What didn't" bullet is useful?
- "Some questions were hard"
* "Arabizi questions (9adeh el kra) retrieve nothing: 0/6 in the sample"
- "The model wasn't good enough"
- "More work is needed"
> Concrete, countable, with an example. The next phase can act on it.
:::

:::mistake
Hiding the failures to make Phase 1 look finished. Your Phase 2 plan comes from the failures; a report without them gives you nothing to plan with.
:::

:::cards
Report opens with? :: One sentence and one key number.
A number needs? :: Its context: dataset, sample size, level, k.
Each "worked" bullet? :: Tied to a number in the table.
Each "didn't" bullet? :: A concrete failure, ideally with an example.
Why write it? :: Phase 2 plan, interviews, and the update to Anis.
:::

:::explain Explain Phase 1 to Anis in four sentences: what you built, the key number, the main failure, the next step.
:::
""",
    "files": [
        lab("day42", "phase1_report.md", task=0),
    ],
    "tasks": [
        "phase1_report.md: one page with a results table and honest failures",
        "Beat the Week 6 boss (8/10)",
        "Retro in notes: what Phase 1 taught you; push everything to GitHub",
    ],
    "done_when": "Phase 1 report committed and 8/10 on the boss.",
    "resources": [],
    "quiz": [
        {"q": "Which result line is most useful?", "options": ["'Retrieval is good'", "'recall@5 = 0.84'", "'recall@5 = 0.84 on 100 ARCD questions, document level'", "'84%'"], "answer": 2,
         "explain": "A number travels only with its context."},
    ],
    "retest": [
        {"q": "Why deduplicate ARCD contexts before indexing?", "options": ["To save disk", "Many questions share a paragraph; duplicates pollute the top k", "The API needs it", "To remove Arabic"], "answer": 1,
         "explain": "One paragraph, one document, many questions pointing to it."},
        {"q": "json.dumps of Arabic text should use...", "options": ["ensure_ascii=True", "ensure_ascii=False", "indent=4", "sort_keys=True"], "answer": 1,
         "explain": "Otherwise the file is full of \\u escapes."},
        {"q": "أ, إ and آ are normalized to...", "options": ["ء", "ا", "ى", "Nothing"], "answer": 1,
         "explain": "Plain alef."},
        {"q": "You normalize documents but not queries. Result?", "options": ["Better recall", "Keyword matches fail on the variants", "No effect", "Faster search"], "answer": 1,
         "explain": "Both sides, same function."},
        {"q": "What does light stemming remove from والمدرسة?", "options": ["Nothing", "The prefix وال", "The last letter", "All vowels"], "answer": 1,
         "explain": "و (and) + ال (the)."},
        {"q": "Why keep a minimum stem length?", "options": ["Speed", "To avoid eating real letters of short words", "Memory", "Embeddings need it"], "answer": 1,
         "explain": "ولد must stay ولد."},
        {"q": "Which token is Arabizi?", "options": ["2025", "9adeh", "prix", "S+2"], "answer": 1,
         "explain": "9 stands for ق, glued to Latin letters."},
        {"q": "Which character must an Arabic sentence splitter know?", "options": ["¿", "؟", "¡", "§"], "answer": 1,
         "explain": "The Arabic question mark (and ؛)."},
        {"q": "Recall at document level means...", "options": ["Counting chunks", "Mapping retrieved chunks to their documents, then recall@k", "Using bigger chunks", "Recall of the LLM"], "answer": 1,
         "explain": "ARCD's truth is the paragraph."},
        {"q": "recall@5 goes from 0.70 to 0.73 on 100 questions. Best reading?", "options": ["Clearly better", "Possibly noise: look at the flipped questions", "Worse", "Meaningless"], "answer": 1,
         "explain": "3 questions can flip by chance; Week 10 adds confidence intervals."},
    ],
}

WEEK6 = {
    "n": 6, "phase": "Phase 1", "title": "Real Arabic data", "dates": "Nov 9-15",
    "goal": "Arabic RAG prototype with eval numbers.",
    "gate": "Arabic RAG prototype with eval numbers",
    "days": [DAY36, DAY37, DAY38, DAY39, DAY40, DAY41, DAY42],
}
