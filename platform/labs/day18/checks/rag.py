CH = [{"id": "c3", "heading": "Visits", "text": "Visits are free."},
      {"id": "c6", "heading": "Augmentation du loyer", "text": "Max 5% par an."}]

ctx = lambda: fn("format_context")(CH)
check("format_context numbers sources from [1]", lambda: ctx().startswith("[1] Visits") and "[2] Augmentation du loyer" in ctx())
check("format_context includes every text", lambda: "Visits are free." in ctx() and "Max 5% par an." in ctx())
p = lambda: fn("build_prompt")("Can the rent go up 8%?", CH)
check("the prompt contains the sources and the question", lambda: "[2] Augmentation du loyer" in p() and "Can the rent go up 8%?" in p())
check("the prompt contains the exact IDK sentence", lambda: var("IDK") in p(), "Write the rule with the IDK constant: f'... reply exactly: {IDK}'")
check("the prompt asks for citations like [1]", lambda: "[1]" in p().replace("[1] Visits", ""))
pc = fn("parse_citations")
check("parse_citations('[2] and [1][2]') -> [1, 2]", lambda: pc("[2] and [1][2]") == [1, 2])
check("parse_citations ignores text without citations", lambda: pc("no sources here") == [])


def run(reply):
    seen = {}

    def retrieve(q, k):
        seen["k"] = k
        return CH

    def model(prompt):
        seen["prompt"] = prompt
        return reply
    return fn("answer")("Can the rent go up 8%?", retrieve, model, k=2), seen


check("answer maps [2] to the chunk id c6", lambda: run("No, max 5% [2].")[0]["sources"] == ["c6"] and run("No, max 5% [2].")[0]["valid"] is True)
check("answer passes k to retrieve and sends the full prompt", lambda: run("x [1]")[1]["k"] == 2 and "[1] Visits" in run("x [1]")[1]["prompt"])
check("a citation that isn't a source -> valid False", lambda: run("Yes [7].")[0]["valid"] is False)
check("no citation and not IDK -> valid False", lambda: run("Yes, of course.")[0]["valid"] is False)
check("the IDK answer is valid with no sources", lambda: run(var("IDK"))[0] == {"answer": var("IDK"), "sources": [], "valid": True})
