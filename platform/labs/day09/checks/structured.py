Listing = var("Listing")
good = '{"price_tnd": 250000, "surface_m2": 120, "rooms": 3, "city": "Sousse"}'
bad = '{"price_tnd": 250000, "surface_m2": 120, "rooms": "three", "city": "Sousse"}'

check("Listing has the four fields",
      lambda: set(Listing.model_fields) == {"price_tnd", "surface_m2", "rooms", "city"})
check("missing values are allowed (None)",
      lambda: Listing(price_tnd=None, surface_m2=None, rooms=None, city=None).rooms is None,
      "Annotate each field as `float | None`, `int | None`, `str | None`.")
parse = fn("parse_listing")
check("parse_listing accepts a valid JSON", lambda: parse(good)[0].rooms == 3 and parse(good)[1] is None)
check("parse_listing returns the error for rooms='three'",
      lambda: parse(bad)[0] is None and "rooms" in str(parse(bad)[1]), "Catch ValidationError and return str(e).")
check("parse_listing handles non-JSON text", lambda: parse("Sure! Here it is:")[0] is None)

prompt = fn("build_prompt")
check("the prompt includes the schema fields and the listing",
      lambda: all(k in prompt("Appart S+3 Sousse") for k in ("price_tnd", "rooms", "Appart S+3 Sousse")))
check("the retry prompt includes the error", lambda: "rooms: bad int" in prompt("x", error="rooms: bad int"))


def run(replies):
    seen = []

    def fake_model(p):
        seen.append(p)
        return replies[len(seen) - 1]
    listing, attempts = fn("extract")("Appart S+3", fake_model)
    return listing, attempts, seen


check("extract: valid on the first try uses 1 attempt", lambda: run([good])[1] == 1 and run([good])[0].city == "Sousse")
check("extract: bad then good uses 2 attempts and returns the listing",
      lambda: run([bad, good])[1] == 2 and run([bad, good])[0] is not None)
check("extract: the retry prompt carries the validation error", lambda: "rooms" in run([bad, good])[2][1])
check("extract: gives up after one retry", lambda: run([bad, bad, good])[:2] == (None, 2),
      "Only one retry: return (None, 2) if the second answer is also invalid.")
