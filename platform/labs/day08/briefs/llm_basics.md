# First API calls
**Topic:** every call is billed in input and output tokens.

## Real example
A bookshop wants to know what it costs to auto-write a 1-line blurb for 5,000 books. Same two ideas as your exercise: **one call = input + output tokens**, and **log every call**. Here the model is faked so you can run it right now:

```python
from types import SimpleNamespace as NS

def fake_create(**kw):  # stands in for client.messages.create
    reply = "A cosy mystery set in old Tunis."
    return NS(content=[NS(text=reply)], usage=NS(input_tokens=len(kw["messages"][0]["content"]) // 4, output_tokens=9))

PRICE_IN, PRICE_OUT = 0.30, 2.50   # $ per million tokens
msg = fake_create(model="auto", max_tokens=60, system="Write one-line blurbs.",
                  messages=[{"role": "user", "content": "Blurb for: 'Murder in the Medina', a detective novel."}])
text, tin, tout = msg.content[0].text, msg.usage.input_tokens, msg.usage.output_tokens
cost = (tin * PRICE_IN + tout * PRICE_OUT) / 1_000_000
print(f"in={tin} out={tout} cost=${cost:.6f} | {text}")
print(f"5,000 books: ${5000 * cost:.2f}")
```

Notice: the cost formula, unpacking `content[0].text` and `usage`, and one log line per call. Your exercise does the same with a real model.

## Your mission
Call a model, log tokens and cost for every call, and compare temperatures.

## Steps
1. Keep `MODEL = "auto"` (uses ⚙ AI) and set both prices from a paid model's pricing page, to practise.
2. `call_cost`: `(tokens_in * price_in + tokens_out * price_out) / 1_000_000`.
3. `ask`: one `client.messages.create(...)` call (shape in the docstring); return text and both token counts.
4. Pick a free model in **⚙ AI** (header), press **Save and test**, then **Run** here.

## Done when
**Check** confirms the cost maths and the logging (no API call needed).
