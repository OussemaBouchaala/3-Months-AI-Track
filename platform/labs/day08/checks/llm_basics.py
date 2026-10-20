cost = fn("call_cost")
check("call_cost(500, 200, 3, 15) is $0.0045", lambda: approx(cost(500, 200, 3, 15), 0.0045),
      "(tokens_in * price_in + tokens_out * price_out) / 1_000_000")
check("1,000 such calls cost $4.50", lambda: approx(1000 * cost(500, 200, 3, 15), 4.5))
check("output tokens are priced separately", lambda: approx(cost(0, 1_000_000, 3, 15), 15))
check("call_cost uses your price constants by default",
      lambda: approx(cost(1_000_000, 0), var("PRICE_IN_PER_M")))


class FakeUsage:
    input_tokens, output_tokens = 12, 7


class FakeMsg:
    content = [type("Block", (), {"text": "Dar El Bahr"})()]
    usage = FakeUsage()


class FakeMessages:
    def __init__(self):
        self.kwargs = None

    def create(self, **kwargs):
        self.kwargs = kwargs
        return FakeMsg()


class FakeClient:
    def __init__(self):
        self.messages = FakeMessages()


fake = FakeClient()


def ask_fake():
    return fn("ask")(fake, "hi", system="be brief", temperature=0.7)


check("ask returns (text, tokens_in, tokens_out)", lambda: tuple(ask_fake()) == ("Dar El Bahr", 12, 7),
      "Skip this one if you use OpenAI: it tests the Anthropic response shape.")
check("ask sends the system prompt and temperature",
      lambda: (ask_fake(), fake.messages.kwargs)[1]["system"] == "be brief" and fake.messages.kwargs["temperature"] == 0.7)
check("log_call prints tokens and cost", lambda: "cost=$" in printed(fn("log_call"), "x", 10, 5)[1])
