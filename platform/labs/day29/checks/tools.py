from pydantic import BaseModel

TOOLS = var("TOOLS")
check("the two agency tools are registered", lambda: {"rental_fee", "deposit"} <= set(TOOLS))
check("@tool returns the function unchanged", lambda: ns["rental_fee"](1000) == {"fee_tnd": 1000})


class PingArgs(BaseModel):
    n: int


def make_ping():
    @fn("tool")("ping", "Echo n", PingArgs)
    def ping(n):
        if n < 0:
            raise ValueError("n must be >= 0")
        return n * 2
    return ping


check("@tool registers fn, args and description", lambda: (make_ping(), TOOLS["ping"]["args"] is PingArgs and TOOLS["ping"]["description"] == "Echo n")[1])
sch = lambda: fn("tool_schema")("deposit")
check("tool_schema has name, description, input_schema", lambda: sch()["name"] == "deposit" and "2 months" in sch()["description"]
      and set(sch()["input_schema"]["properties"]) == {"monthly_rent", "has_pet"})
d = fn("dispatch")
check("dispatch runs a valid call", lambda: (make_ping(), d("ping", {"n": 3}))[1] == {"ok": True, "result": 6})
check("dispatch refuses unknown tools", lambda: d("rm_rf", {}) == {"ok": False, "error": "unknown tool: rm_rf"})
check("dispatch reports invalid arguments", lambda: (make_ping(), d("ping", {"n": "lots"}))[1]["ok"] is False and d("ping", {"n": "lots"})["error"].startswith("invalid arguments"))
check("dispatch catches errors raised by the tool", lambda: (make_ping(), d("ping", {"n": -1}))[1] == {"ok": False, "error": "ValueError: n must be >= 0"})
pa = fn("parse_action")
check("parse_action: tool call with text around it", lambda: pa('OK! {"tool": "deposit", "args": {"monthly_rent": 900}} done') == ("tool", "deposit", {"monthly_rent": 900}))
check("parse_action: final answer", lambda: pa('{"answer": "2,250 TND"}') == ("answer", "2,250 TND"))
check("parse_action: garbage -> invalid", lambda: pa("I will now call the tool")[0] == "invalid" and pa('{"tool": ')[0] == "invalid" and pa('{"foo": 1}')[0] == "invalid")
check("deposit: 2 months, +0.5 with a pet", lambda: d("deposit", {"monthly_rent": 900}) == {"ok": True, "result": {"deposit_tnd": 1800}}
      and d("deposit", {"monthly_rent": 900, "has_pet": True})["result"] == {"deposit_tnd": 2250})
