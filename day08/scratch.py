def call_cost(tokens_in, tokens_out, price_in_per_m, price_out_per_m):
    return (tokens_in * price_in_per_m + tokens_out * price_out_per_m) / 1_000_000

# 1,000 calls of 500 input + 200 output tokens at $3 / $15 per million
print(f"${1000 * call_cost(500, 200, 3, 15):.2f}")
