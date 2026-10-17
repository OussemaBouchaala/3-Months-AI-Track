# Week 2 project: Document extraction service: messy real estate listings (Arabic, French, English) to clean JSON.
# Check tests call_cost and the logging without calling any API.
# Run makes real API calls: set LLM_API_KEY in your terminal, then restart Bench.

MODEL = "qwen/qwen3.8-27b"  # TODO: a small, cheap model from your provider's model list
PRICE_IN_PER_M = 1.00       # TODO: your model's input price in $ per 1M tokens
PRICE_OUT_PER_M = 5.00      # TODO: your model's output price in $ per 1M tokens


def call_cost(tokens_in, tokens_out, price_in_per_m=PRICE_IN_PER_M, price_out_per_m=PRICE_OUT_PER_M):
    """Dollar cost of one call: input and output tokens are billed separately, per million."""
    # TODO
    return (tokens_in * price_in_per_m + tokens_out * price_out_per_m) / 1_000_000


def ask(client, prompt, system="You are a concise assistant.", temperature=0.0):
    """Send ONE user message with a system prompt. Return (text, tokens_in, tokens_out).
    Anthropic SDK:
        msg = client.messages.create(model=MODEL, max_tokens=200, system=system,
                                     temperature=temperature,
                                     messages=[{"role": "user", "content": prompt}])
        text = msg.content[0].text;  tokens: msg.usage.input_tokens / msg.usage.output_tokens"""
    # TODO
    kwargs = dict(model=MODEL, max_tokens=200, system=system,
                  messages=[{"role": "user", "content": prompt}])
    if temperature:                      # only send it when it isn't the default
        kwargs["temperature"] = temperature
    msg = client.messages.create(**kwargs)
    return msg.content[0].text, msg.usage.input_tokens, msg.usage.output_tokens


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
