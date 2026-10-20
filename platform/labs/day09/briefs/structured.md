# JSON you can trust
**Topic:** schema in the prompt, validation on the way out, one retry with the error.

## Real example
An HR team extracts candidate info from CVs. The model is faked: the first answer is broken, the second is fixed after seeing the error. This is exactly the "validate, retry once with the error" loop you'll build:

```python
from pydantic import BaseModel, ValidationError

class Candidate(BaseModel):
    name: str
    years_experience: int | None

answers = iter(['{"name": "Amira", "years_experience": "five"}', '{"name": "Amira", "years_experience": 5}'])
fake_model = lambda prompt: next(answers)

def extract(text, call_model):
    error = None
    for attempt in (1, 2):
        prompt = f"JSON only, schema {Candidate.model_json_schema()}\n{text}" + (f"\nFix this error: {error}" if error else "")
        try:
            return Candidate.model_validate_json(call_model(prompt)), attempt
        except ValidationError as e:
            error = e.errors()[0]["msg"]
            print(f"attempt {attempt} failed: {error}")
    return None, 2

print(extract("Amira, 5 years as a data analyst", fake_model))
```

## Your mission
Turn listing text into a validated `Listing`, with one automatic retry.

## Steps
1. Fill `listings.json` with 10 real listings and your labels.
2. `Listing`: four optional fields.
3. `parse_listing`: `model_validate_json`, catch `ValidationError`.
4. `build_prompt`: the schema, the listing, and the previous error if any.
5. `extract`: try, retry once with the error, return `(listing, attempts)`.

Tip for `call_model`: `from bench_llm import get_client` and reuse `ask()` from day08, so it runs on your free model.

## Done when
**Check** runs `extract` against fake models: valid, fixed on retry, and failing.
