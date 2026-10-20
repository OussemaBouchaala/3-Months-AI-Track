"""Week 8: Build I, ingestion and retrieval end to end (Nov 23-29, 2026)."""
from lab_files import lab

DAY50 = {
    "id": "w8d1", "folder": "day50", "date": "2026-11-23", "weekday": "Mon",
    "title": "Parsing real documents", "minutes": 75,
    "why": "Your client's knowledge is locked in PDFs, Word files and web pages. Bad parsing quietly poisons everything after it.",
    "lesson": r"""
:::hook
The agency sends you a folder: `reglement.pdf`, `grille_tarifs.docx`, `contrat_42.docx` (actually a PDF someone renamed), and a page saved from their website. Your Week 3 code read one Markdown file. Today it reads all of these, and doesn't stop at the first broken one.
:::

## Trust bytes, not names

File extensions lie. The first bytes don't:
- `%PDF` → PDF
- `PK\x03\x04` → a zip (`.docx`, `.xlsx`, `.pptx` are all zips)
- `<` → probably HTML

```python
for name, head in [("contrat_42.docx", b"%PDF-1.7"), ("tarifs.docx", b"PK\x03\x04"), ("page.html", b"<!doctype")]:
    kind = "pdf" if head.startswith(b"%PDF") else "zip" if head.startswith(b"PK") else "html" if head.startswith(b"<") else "?"
    print(f"{name:16} -> {kind}")
```

:::analogy
A customs officer opens the box. The label says "books"; the officer checks what's inside before deciding which form to fill.
:::

## Each format, the light way

- **docx**: a zip; text lives in `word/document.xml`, one `<w:p>` per paragraph, text in `<w:t>` pieces. `zipfile` + `ElementTree`, no library needed.
- **HTML**: `html.parser`; skip `<script>` and `<style>`; newline on block tags.
- **PDF with a text layer**: `pypdf`. Scans (no text layer) come tomorrow.

## Clean what you can't see

Exported Arabic text is full of invisible characters: RLM marks (`‏`), zero-width spaces, a BOM. And old PDFs use Arabic **presentation forms** (`ﻻ` as one code point instead of `ل` + `ا`). `unicodedata.normalize("NFKC", text)` fixes the second; a small translate table removes the first.

:::predict "الضمان" copied from a PDF doesn't match "الضمان" typed by the user, though they look identical. Likely cause?
---
Invisible characters (RLM, zero-width) or presentation forms in the PDF text. Print `[hex(ord(c)) for c in word]` to see them; NFKC plus removing invisible marks makes them equal.
:::

:::check
? One file in 120 raises an exception during parsing. What should the batch do?
- Stop and fix it before continuing
* Record it in a skipped list with the reason, and continue
- Ignore it silently
- Retry it forever
> A batch that dies on file 37 indexes nothing. A batch that logs and continues indexes 119 and tells you what to fix.
:::

:::mistake
Trusting that all files are UTF-8. Old Windows exports can be cp1256 (Arabic Windows) or cp1252. `errors="replace"` keeps the batch alive; then search for `�` in the output to find files to re-decode.
:::

:::cards
Magic bytes of a PDF? :: %PDF
What is a .docx inside? :: A zip with word/document.xml.
NFKC does what for Arabic? :: Turns presentation forms (ﻻ) into normal letters.
RLM? :: ‏, an invisible right-to-left mark.
A broken file in a batch? :: Skip it with a reason; continue.
:::

:::explain Explain why a file named contrat.docx might fail to open as Word, and how your parser handles it.
:::
""",
    "files": [
        lab("day50", "parse_docs.py", task=[0, 1]),
    ],
    "tasks": [
        "parse_docs.py: detect_type, html_to_text, docx_to_text",
        "clean_text and parse_file; run on your client's folder",
        "List the skipped files and the 5 shortest texts: those are your scans",
    ],
    "done_when": "Every document is in parsed.jsonl or in the skipped list with a reason.",
    "resources": [{"label": "Python: html.parser", "url": "https://docs.python.org/3/library/html.parser.html"},
                  {"label": "pypdf", "url": "https://pypdf.readthedocs.io/"}],
    "quiz": [
        {"q": "contrat.docx starts with %PDF. What is it?", "options": ["A Word file", "A PDF with the wrong extension", "A zip", "Corrupted"], "answer": 1,
         "explain": "Magic bytes beat extensions."},
        {"q": "What does NFKC normalization fix in Arabic PDFs?", "options": ["Diacritics", "Presentation forms like ﻻ", "Right-to-left order", "Digits"], "answer": 1,
         "explain": "Compatibility forms become standard letters."},
    ],
}

DAY51 = {
    "id": "w8d2", "folder": "day51", "notes_task": 2, "date": "2026-11-24", "weekday": "Tue",
    "title": "OCR for scans", "minutes": 75,
    "why": "Most signed contracts are scans. Without OCR they're invisible to search, and nobody notices until a client asks.",
    "lesson": r"""
:::hook
80 of the agency's 120 documents are scanned contracts. pypdf returns an empty string for each page. Your index has 40 documents, your smoke test still passes (its questions hit the rules PDF), and the first real question about a contract gets "I don't know".
:::

## Per page: text layer or OCR

Some PDFs mix both: typed pages and a scanned signature page. Decide **per page**: if the text layer has fewer than ~50 letters, OCR that page.

```python
pages = ["Article 1. Le loyer mensuel est fixé à 900 TND, payable avant le 5 du mois.", "", "  3 / 12 "]
for i, t in enumerate(pages, 1):
    letters = sum(c.isalpha() for c in t)
    print(f"page {i}: {letters:3} letters -> {'text' if letters >= 50 else 'OCR'}")
```

## Tesseract with Arabic and French

`pytesseract.image_to_string(image, lang="ara+fra")` at 300 DPI. Arabic OCR is weaker than French: expect errors in diacritics and joined letters. That's why you **measure** quality per page and flag the bad ones instead of trusting the output.

:::analogy
A typist copying old handwritten letters. Most pages are fine; some are smudged. A good typist marks "[illegible]" instead of guessing; your pipeline marks low-quality pages for a human.
:::

## Layout noise

Every page repeats "Dar Yasmine - Contrat de location" and ends with "- 3 -". Left in, that header ends up in every chunk and every embedding, so every chunk looks a bit similar to every query about contracts. Remove lines that appear on most pages, and page-number lines. Join words hyphenated across lines (`loca-\ntion`).

:::predict A quality score of 0.70 on a page. What do you do with it?
---
Index it (some text beats none), but flag it: log the page, and consider a manual check or a re-scan. Later you can see whether failures in Week 10 come from these pages.
:::

:::check
? Why inject `ocr_fn` instead of calling Tesseract inside process_pages?
- Tesseract is slow
* So the logic is testable without Tesseract installed, and the OCR engine can be swapped
- It's shorter
- Python requires it
> Same dependency injection as the service on Saturday.
:::

:::mistake
OCR at the default 72 DPI. Arabic letters lose their dots and the error rate explodes. Render pages at 300 DPI before OCR.
:::

:::cards
When to OCR a page? :: When its text layer has almost no letters.
Tesseract languages for the agency? :: lang="ara+fra"
DPI for OCR? :: 300
Header on every page? :: Remove it; it pollutes every chunk.
Low quality score? :: Index but flag for a human.
:::

:::explain Explain to the agency manager why some contracts might be answered less reliably than others.
:::
""",
    "files": [
        lab("day51", "ocr_pipeline.py", task=[0, 1]),
    ],
    "tasks": [
        "ocr_pipeline.py: needs_ocr, text_quality, dehyphenate",
        "remove_repeated_lines and process_pages with an injected OCR function",
        "Install Tesseract (ara + fra); OCR one real scan and note its quality per page",
    ],
    "done_when": "Your scans produce text, and you know which pages are below 0.9 quality.",
    "resources": [{"label": "Tesseract on Windows (UB Mannheim)", "url": "https://github.com/UB-Mannheim/tesseract/wiki"},
                  {"label": "pytesseract", "url": "https://pypi.org/project/pytesseract/"}],
    "quiz": [
        {"q": "A PDF has typed pages and one scanned page. Best approach?", "options": ["OCR everything", "Decide per page", "Skip the scan", "Use only pypdf"], "answer": 1,
         "explain": "OCR where the text layer is empty."},
        {"q": "Why remove repeated headers?", "options": ["Save disk", "They make every chunk look alike to embeddings", "Legal reasons", "OCR needs it"], "answer": 1,
         "explain": "Shared noise blurs similarity."},
    ],
}

DAY52 = {
    "id": "w8d3", "folder": "day52", "date": "2026-11-25", "weekday": "Wed",
    "title": "Chunks with metadata", "minutes": 75,
    "why": "A chunk that knows its document and section can be filtered, cited and debugged. One that doesn't is just text.",
    "lesson": r"""
:::hook
The model answers "Deux mois [3]". The UI shows source [3]: "Deux mois de loyer." Which contract? Which article? The agent can't show it to the client. The chunk had the text, but lost its address.
:::

## Metadata on every chunk

| Field | Why |
|---|---|
| doc_id | delete and re-index a document; cite it |
| section | "Article 4 - Caution" in the citation |
| lang | filter, route, measure per language |
| hash | find the same clause in 40 contracts |
| embed_text | title > section + text, for better embeddings |

## Sections from headings

Contracts have structure: "Article 4", "المادة 4", "## Fees". Track the current heading while reading lines, and attach it to every chunk below it.

```python
import re
HEADING = re.compile(r"^(Article\s+\d+.*|المادة\s+\S+.*)$")
section = ""
for line in ["Article 3 - Loyer", "900 TND par mois.", "المادة 4 الضمان", "شهرين."]:
    if HEADING.match(line):
        section = line
    else:
        print(f"[{section}] {line}")
```

:::analogy
A photocopied page from a law book is useless without "Code des obligations, article 245" written at the top. Same text, but now you can cite it.
:::

## Contextual headers for embeddings

"Deux mois." alone embeds as "something about two months". "Bail type > Article 4 - Caution\nDeux mois." embeds as "deposit, lease, two months". Prepend title and section to the text you **embed**; keep the plain text for display.

:::predict 40 contracts share the same Article 7 word for word. Without dedupe, a question about Article 7 returns...
---
Five copies of the same clause in the top 5, pushing out everything else. Hash the normalized text and keep one copy (with a note of how many documents share it, if you need that).
:::

:::check
? What should the embedding see for a chunk?
- Only the chunk text
* The title and section header plus the chunk text
- Only the title
- The whole document
> Context in the header, content in the body: better vectors, same display.
:::

:::mistake
Chunk ids from a counter across the whole corpus (`c0` … `c9999`). Re-index one document and every id after it shifts. Use `doc_id-cN`: stable per document.
:::

:::cards
doc_id in a chunk? :: To cite, filter and re-index one document.
Contextual header? :: "title > section" prepended to the embedded text.
Content hash? :: Finds duplicates like the same clause in 40 contracts.
Stable chunk id? :: doc_id-cN, numbered within the document.
What's displayed? :: The plain chunk text, not the header.
:::

:::explain Explain why "Deux mois." embeds badly on its own, and the fix.
:::
""",
    "files": [
        lab("day52", "chunk_meta.py", task=[0, 1]),
    ],
    "tasks": [
        "chunk_meta.py: split_sections, content_hash",
        "make_chunks with contextual headers; dedupe_chunks",
        "Adjust HEADING to your documents; check most chunks get a section",
    ],
    "done_when": "chunks.json has sections, languages and hashes; duplicates are counted.",
    "resources": [{"label": "Anthropic: contextual retrieval", "url": "https://www.anthropic.com/news/contextual-retrieval"}],
    "quiz": [
        {"q": "Why ids like bail7-c3 instead of a global counter?", "options": ["Shorter", "Stable when another document is re-indexed", "Faster search", "Required by pgvector"], "answer": 1,
         "explain": "A global counter shifts on every change."},
        {"q": "The same clause in 40 contracts. Without dedupe...", "options": ["Better recall", "Copies crowd the top k", "Nothing changes", "Faster search"], "answer": 1,
         "explain": "Five identical results tell you one thing."},
    ],
}

DAY53 = {
    "id": "w8d4", "folder": "day53", "notes_task": 2, "date": "2026-11-26", "weekday": "Thu",
    "title": "Incremental indexing", "minutes": 75,
    "why": "Documents change every week. Re-embedding everything each time is slow, costly, and makes you avoid updating.",
    "lesson": r"""
:::hook
Monday the agency adds two contracts and updates the fee grid. Your indexer re-embeds all 120 documents: 25 minutes on the office PC. Next week you "forget" to run it, and the assistant quotes last month's fees.
:::

## The manifest

After each run, save `{file name: sha256 of its bytes}`. Next run, compare:

```python
old = {"reglement.pdf": "a1", "tarifs.docx": "b2", "bail_old.pdf": "c3"}
new = {"reglement.pdf": "a1", "tarifs.docx": "b9", "bail_43.pdf": "d4"}
print("add", sorted(set(new) - set(old)))
print("update", sorted(n for n in set(new) & set(old) if new[n] != old[n]))
print("delete", sorted(set(old) - set(new)))
```

Only the 3 changed files get work.

:::analogy
A librarian with an inventory list. New books get shelved, replaced editions get swapped, missing books get removed from the catalog. Nobody re-shelves the whole library because two books arrived.
:::

## Order matters for updates

An updated file: **delete its old chunks first**, then index the new version. Otherwise both versions live in the index and the model may quote the old fee next to the new one.

## Batches

Embed in batches (32 texts per call) and insert with `executemany`. One call per chunk is slow; one call for 5,000 chunks hits memory or timeouts.

:::predict The indexer crashes halfway. You saved the manifest at the start. What happens next run?
---
The files that never got indexed look "unchanged" and are skipped forever. Save the manifest **after** success, never before.
:::

:::check
? Why hash the content rather than use the file's modified date?
- Dates are slower to read
* Copying or touching a file changes its date but not its content
- Hashes are shorter
- Windows has no dates
> Content hash: re-index only when the content really changed.
:::

:::mistake
Forgetting deletions. A contract removed from the folder stays in the index, and the assistant cites a document that no longer exists.
:::

:::cards
Manifest? :: {file name: content hash} from the last successful run.
Updated file? :: Delete old chunks, then index the new version.
When to save the manifest? :: After the run succeeds.
Why batches? :: Fewer calls than one per chunk, less memory than one huge call.
Deleted file? :: Remove its chunks from the index.
:::

:::explain Explain to the agency what happens when they replace the fee grid in the folder.
:::
""",
    "files": [
        lab("day53", "indexer.py", task=[0, 1]),
    ],
    "tasks": [
        "indexer.py: file_hash, build_manifest, plan",
        "batched and apply_plan; index your client's folder into project_chunks",
        "Run twice (0 indexed), edit a file, run again (1 updated)",
    ],
    "done_when": "Re-running on an unchanged folder indexes nothing; an edited file is re-indexed once.",
    "resources": [{"label": "psycopg: executemany", "url": "https://www.psycopg.org/psycopg3/docs/api/cursors.html"}],
    "quiz": [
        {"q": "Re-indexing an updated file, first step?", "options": ["Insert new chunks", "Delete its old chunks", "Drop the table", "Re-embed everything"], "answer": 1,
         "explain": "Otherwise old and new versions coexist."},
        {"q": "When should the manifest be saved?", "options": ["At the start", "After a successful run", "Never", "Every minute"], "answer": 1,
         "explain": "A crash must not mark unindexed files as done."},
    ],
}

DAY54 = {
    "id": "w8d5", "folder": "day54", "date": "2026-11-27", "weekday": "Fri",
    "title": "Citations you can trust", "minutes": 75,
    "why": "An agent will show the citation to a client. A wrong or decorative citation is worse than none.",
    "lesson": r"""
:::hook
"La caution est de deux mois [1]. Le chat doit être vacciné [2]." Source [2] says the deposit goes up half a month with a pet. Nothing about vaccines. The citation is real; the claim isn't in it. Day 18 would have marked this answer valid.
:::

## Three checks, cheapest first

1. **Format**: models write `[1, 2]`, `[1][2]`, `[1] [2]`. Normalize to one form.
2. **Range**: `[7]` with 5 sources is invented. Remove it, and log it.
3. **Support**: does the cited chunk contain the sentence's content words?

```python
import re
words = lambda t: {w for w in re.findall(r"\w+", t.lower()) if len(w) >= 4}
source = "Avec un animal, la caution augmente d'un demi-mois."
for claim in ["Avec un animal la caution augmente.", "Le chat doit être vacciné."]:
    share = len(words(claim) & words(source)) / len(words(claim))
    print(f"{share:.2f}", claim)
```

:::analogy
A teacher checking a student's references. Does the book exist (range)? Is the quote on that page (support)? The second check catches the student who cites real books for things they made up.
:::

## Coverage

Split the answer into sentences; count those with a citation. An answer with 4 sentences and 1 citation has 0.25 coverage: three claims nobody can check. Log coverage for every answer; it's a free quality signal.

:::predict Word overlap says a sentence is supported. Can it still be wrong?
---
Yes: "the deposit is NOT refundable" overlaps perfectly with "the deposit is refundable". Overlap catches unrelated citations, not negations or wrong numbers. In Week 10 an LLM judge checks faithfulness more carefully.
:::

:::check
? Which answer is most trustworthy?
- Long, fluent, one citation at the end
* Short, every sentence cited, each citation supporting its sentence
- No citations but confident
- Many citations, some out of range
> Coverage and support, not fluency.
:::

:::mistake
Showing `[3]` in the UI without the source text. The agent can't verify it, and neither can the client. Render each cited source with title, section and the chunk.
:::

:::cards
Normalize markers? :: [1, 2] and [1] [2] become [1][2].
Out-of-range marker? :: Remove it and log it.
Citation coverage? :: Share of sentences with at least one citation.
Support check? :: Content-word overlap between sentence and cited chunk.
Overlap's blind spot? :: Negations and wrong numbers.
:::

:::explain Explain the difference between a citation that exists and a citation that supports the claim.
:::
""",
    "files": [
        lab("day54", "citations.py", task=[0, 1]),
    ],
    "tasks": [
        "citations.py: normalize_markers, clean_citations, sentence_citations",
        "citation_coverage, unsupported_claims, render_sources",
        "Run 5 real answers through it; note the unsupported ones",
    ],
    "done_when": "The example's invalid marker and invented sentence are both caught.",
    "resources": [],
    "quiz": [
        {"q": "[7] appears with 5 sources. What do you do?", "options": ["Keep it", "Remove it and log it", "Renumber it to [5]", "Fail the request"], "answer": 1,
         "explain": "An invented source must not reach the user."},
        {"q": "What does word overlap NOT catch?", "options": ["Unrelated citations", "A negated claim", "Out-of-range numbers", "Missing citations"], "answer": 1,
         "explain": "'not refundable' vs 'refundable' share the words."},
    ],
}

DAY55 = {
    "id": "w8d6", "folder": "day55", "date": "2026-11-28", "weekday": "Sat",
    "title": "The pipeline as a service", "minutes": 180,
    "why": "Next week a UI and a tool call this. One endpoint, testable without a database, is what makes Week 9 easy.",
    "lesson": r"""
:::hook
Your pipeline works in a notebook: parse, OCR, chunk, index, retrieve, answer, check citations. The UI can't call a notebook. The agent's colleague can't either. Today it becomes `POST /ask`.
:::

## Inject the heavy parts

```python
def create_app(retrieve, generate, scrub):
    ...
```

The app doesn't know about Postgres or Ollama. Production passes the real functions; tests pass a list and a lambda. Tests run in a second, without Docker.

:::analogy
A restaurant kitchen with a supplier slot. On weekdays the real supplier delivers; during the health inspection, the inspector brings sample ingredients. The kitchen's procedures are tested either way.
:::

## What /ask does

1. Scrub PII from the question.
2. Retrieve k chunks. **None?** Answer IDK without calling the model (free and fast).
3. Generate. Model down? **503**, not a stack trace.
4. Clean citations; return sources in citation order.
5. Return latency, and a request id header for logs.

```python
import uuid
rid = uuid.uuid4().hex
print(rid, len(rid))
```

:::predict The model raises a timeout. What should the client receive?
---
HTTP 503 "model unavailable". The UI shows "try again in a moment". A 500 with a Python traceback leaks internals and tells the UI nothing useful.
:::

## The request id

Every response gets `X-Request-ID`. When the agent says "the answer at 10:42 was wrong", you search the logs for that id and see the question, the chunks, and the prompt. Week 11 builds on it.

:::check
? Why answer IDK without calling the model when retrieval returns nothing?
- To hide errors
* Nothing to cite means nothing to answer from; skipping the call saves time and money
- The model can't handle empty prompts
- To lower latency only
> Grounded or nothing.
:::

:::mistake
Creating the database connection at import time. The module won't even import without Postgres, so tests fail and the app can't start to show a health check. Build the real wiring in a function.
:::

:::cards
Dependency injection here? :: retrieve and generate passed into create_app.
Empty retrieval? :: IDK, no model call.
Model failure? :: 503 "model unavailable".
X-Request-ID? :: Echoed or created; ties a response to its logs.
Why Pydantic for the body? :: Length limits and k range return 422 automatically.
:::

:::explain Explain dependency injection using your create_app as the example.
:::
""",
    "files": [
        lab("day55", "pipeline_service.py", task=[0, 1]),
    ],
    "tasks": [
        "pipeline_service.py: build_prompt, request id middleware",
        "/ask with scrub, IDK shortcut, 503, citation cleaning, sources",
        "Run it for real and ask 5 golden dev questions at /docs",
    ],
    "done_when": "/ask answers a real question with a source from your documents, and the tests pass without a database.",
    "resources": [{"label": "FastAPI: testing", "url": "https://fastapi.tiangolo.com/tutorial/testing/"},
                  {"label": "FastAPI: middleware", "url": "https://fastapi.tiangolo.com/tutorial/middleware/"}],
    "quiz": [
        {"q": "Why pass retrieve and generate into create_app?", "options": ["Speed", "Tests run with fakes, production with real ones", "FastAPI requires it", "Security"], "answer": 1,
         "explain": "Dependency injection makes the service testable."},
        {"q": "Right status when the model is down?", "options": ["200 with empty answer", "404", "503", "422"], "answer": 2,
         "explain": "Service unavailable: temporary, retry later."},
    ],
}

DAY56 = {
    "id": "w8d7", "folder": "day56", "retest_task": 1, "date": "2026-11-29", "weekday": "Sun",
    "title": "Smoke test and retro", "minutes": 150,
    "why": "Before adding a UI and a tool, prove the path works end to end with one command.",
    "lesson": r"""
:::hook
Wednesday you change the chunker. Thursday a colleague tries the assistant: every answer is IDK. The chunker produced empty texts, and nothing told you. A 30-second smoke test after each change would have.
:::

## Smoke test vs evaluation

| | Smoke test | Evaluation (Week 10) |
|---|---|---|
| Questions | 6-10 | the whole golden test set |
| Question | "is it alive and sane?" | "how good is it?" |
| Time | seconds | minutes to hours |
| When | after every change | per configuration |
| Output | pass/fail, exit code | metrics with confidence |

## What to check

- Status 200, non-empty answer, latency under a limit.
- Answer questions: not IDK, has sources, contains the key fact.
- IDK questions: IDK, no sources.

```python
import sys
results = [("caution", True), ("documents", True), ("cars (idk)", False)]
print(f"{sum(ok for _, ok in results)}/{len(results)} passed")
code = 0 if all(ok for _, ok in results) else 1
print("exit code", code)
```

:::analogy
Switching on a repaired car before the road test: does it start, do the lights work, do the brakes respond? Five checks, one minute. The road test comes later.
:::

:::predict The smoke test passes but a colleague still finds a wrong answer. Did the smoke test fail?
---
No. It's not designed to catch quality issues, only broken paths. Add the colleague's question to the golden set (and maybe to the smoke cases if it reveals a broken path).
:::

:::check
? Why does the smoke test return an exit code?
- For logging
* So scripts and CI can stop automatically when it fails
- Python requires it
- To speed it up
> 0 = go, 1 = stop. Week 11's CI uses it.
:::

:::mistake
Smoke cases that depend on exact wording ("must contain 'deux mois de loyer'"). The model rephrases and the test flakes. Check the key fact ("2" or "deux"), not the sentence.
:::

:::cards
Smoke test size? :: 6-10 cases, seconds to run.
IDK case checks? :: idk true and no sources.
Exit code? :: 0 all passed, 1 otherwise.
When to run? :: After every change, before anyone else uses it.
Flaky check? :: Exact sentences; check key facts instead.
:::

:::explain Explain the difference between your smoke test and the Week 10 evaluation.
:::
""",
    "files": [
        lab("day56", "smoke_test.py", task=0),
    ],
    "tasks": [
        "smoke_test.py: passing against your running service",
        "Beat the Week 8 boss (8/10)",
        "Retro in notes: which stage was hardest on real documents? Push Week 8",
    ],
    "done_when": "Smoke test green against the real service and 8/10 on the boss.",
    "resources": [],
    "quiz": [
        {"q": "A smoke test answers...", "options": ["How accurate is it?", "Is the whole path alive and sane?", "Which model is best?", "How much does it cost?"], "answer": 1,
         "explain": "Quality is Week 10's job."},
    ],
    "retest": [
        {"q": "A file named .docx starts with %PDF. Your parser should...", "options": ["Fail", "Treat it as a PDF", "Treat it as Word", "Skip it"], "answer": 1,
         "explain": "Magic bytes beat extensions."},
        {"q": "Text from a PDF doesn't match identical-looking typed Arabic. First suspect?", "options": ["The model", "Invisible marks or presentation forms", "The database", "The font size"], "answer": 1,
         "explain": "NFKC and removing RLM/zero-width characters."},
        {"q": "When does a page need OCR?", "options": ["Always", "When its text layer has almost no letters", "When it's in Arabic", "Never"], "answer": 1,
         "explain": "Per page, not per document."},
        {"q": "Why remove a header repeated on every page?", "options": ["It's ugly", "It makes all chunks look similar to embeddings", "OCR fails on it", "Legal"], "answer": 1,
         "explain": "Shared noise blurs retrieval."},
        {"q": "What should the embedding model see for a chunk?", "options": ["Text only", "Title > section header + text", "The file name", "The hash"], "answer": 1,
         "explain": "Contextual headers improve vectors."},
        {"q": "Re-indexing an updated file, the first step is...", "options": ["Insert", "Delete its old chunks", "Drop everything", "Rebuild the HNSW index"], "answer": 1,
         "explain": "Otherwise two versions coexist."},
        {"q": "Saving the manifest before indexing risks...", "options": ["Nothing", "Unindexed files marked as done after a crash", "Duplicate ids", "Slow startup"], "answer": 1,
         "explain": "Save after success."},
        {"q": "A sentence cites [2], but source 2 is about something else. Which check catches it?", "options": ["Range check", "Support (overlap) check", "Format check", "Coverage"], "answer": 1,
         "explain": "The citation exists but doesn't support the claim."},
        {"q": "Retrieval returns no chunks. /ask should...", "options": ["Call the model anyway", "Answer IDK without calling the model", "Return 500", "Retry forever"], "answer": 1,
         "explain": "Nothing to ground on."},
        {"q": "The smoke test exits with 1. That means...", "options": ["All passed", "At least one case failed", "It crashed", "The model is slow"], "answer": 1,
         "explain": "Scripts and CI stop on non-zero."},
    ],
}

WEEK8 = {
    "n": 8, "phase": "Phase 2", "title": "Build I", "dates": "Nov 23-29",
    "goal": "Ingestion and retrieval working end to end.",
    "gate": "End-to-end path works",
    "days": [DAY50, DAY51, DAY52, DAY53, DAY54, DAY55, DAY56],
}
