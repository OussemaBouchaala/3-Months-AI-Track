# Week 2 project: Document extraction service: messy real estate listings (Arabic, French, English) to clean JSON.
# Check tests call_cost and the logging without calling any API.
# Run makes real calls with the free model you chose in Bench (⚙ AI in the header). No key in this file.
MODEL = "auto"              # "auto" = the model chosen in ⚙ AI. Or write a model name from "List models".
# Free tiers cost $0, but price it as if you were paying, to learn the habit.
PRICE_IN_PER_M = 0.30       # TODO: a paid model's input price in $ per 1M tokens (e.g. Gemini Flash, Claude Haiku)
PRICE_OUT_PER_M = 2.50      # TODO: its output price in $ per 1M tokens


def call_cost(tokens_in, tokens_out, price_in_per_m=PRICE_IN_PER_M, price_out_per_m=PRICE_OUT_PER_M):
    """Dollar cost of one call: input and output tokens are billed separately, per million."""
    # TODO
    ...


def ask(client, prompt, system="You are a concise assistant.", temperature=0.0):
    """Send ONE user message with a system prompt. Return (text, tokens_in, tokens_out).
    The client from bench_llm has the same shape as the Anthropic SDK:
        msg = client.messages.create(model=MODEL, max_tokens=200, system=system,
                                     temperature=temperature,
                                     messages=[{"role": "user", "content": prompt}])
        text = msg.content[0].text;  tokens: msg.usage.input_tokens / msg.usage.output_tokens"""
    # TODO
    ...


def log_call(text, tokens_in, tokens_out):
    """Print one line with the token counts, cost and the start of the reply. Return the cost."""
    cost = call_cost(tokens_in, tokens_out)
    print(f"in={tokens_in:>5}  out={tokens_out:>5}  cost=${cost:.5f}  | {text[:60]!r}")
    return cost


if __name__ == "__main__":
    from bench_llm import get_client  # Bench's client: Gemini, Groq, Ollama... whatever you chose in ⚙ AI

    client = get_client()

    total = 0.0
    prompt = "Give one creative name for a seaside apartment in Sousse."
    for temperature in (0.0, 0.0, 0.0, 1.0, 1.0, 1.0):
        print(f"temperature={temperature}", end="  ")
        total += log_call(*ask(client, prompt, temperature=temperature))
    print(f"total ${total:.5f}")
