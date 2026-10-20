# Listing text in, validated JSON out. Validate every answer; retry once with the error.
import json

from pydantic import BaseModel, ValidationError


class Listing(BaseModel):
    """The JSON shape you want back. Every field may be missing in a listing, so allow None."""
    # TODO: price_tnd: float | None, surface_m2: float | None, rooms: int | None, city: str | None
    ...


def parse_listing(raw_json):
    """Validate a JSON string with Listing.model_validate_json.
    Return (listing, None) when valid, (None, error_text) when not (catch ValidationError)."""
    # TODO
    ...


def build_prompt(text, error=None):
    """Ask for JSON ONLY that matches the schema (include json.dumps(Listing.model_json_schema())),
    then the listing text. If error is given, add it and ask for a corrected JSON."""
    # TODO
    ...


def extract(text, call_model):
    """call_model(prompt) -> str (the model's raw reply).
    Try once; if parse_listing fails, retry ONCE with the error in the prompt.
    Return (listing_or_None, attempts_used)."""
    # TODO
    ...


def call_model(prompt):
    """Your real model call: reuse ask() from day08 (or your provider SDK) and return the reply text."""
    # TODO
    ...


if __name__ == "__main__":
    listings = json.load(open("listings.json", encoding="utf-8"))
    first, after_retry, failed = 0, 0, 0
    for item in listings:
        listing, attempts = extract(item["text"], call_model)
        if listing is None:
            failed += 1
        elif attempts == 1:
            first += 1
        else:
            after_retry += 1
        print(attempts, listing)
    print(f"first try: {first}  after retry: {after_retry}  failed: {failed}")
