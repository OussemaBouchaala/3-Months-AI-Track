import json

schemas = [{"name": "deposit", "description": "Deposit: 2 months", "input_schema": {"type": "object", "properties": {"monthly_rent": {"type": "number"}}}}]
sp = lambda: fn("system_prompt")(schemas)
check("system_prompt lists each tool and its schema", lambda: "deposit" in sp() and "Deposit: 2 months" in sp() and "monthly_rent" in sp())
check("system_prompt explains both reply formats", lambda: '"tool"' in sp() and '"answer"' in sp())


def scripted(replies):
    seen = []

    def model(system, messages):
        seen.append((system, [dict(m) for m in messages]))
        return replies[min(len(seen), len(replies)) - 1]
    return model, seen


calls = []


def dispatch(name, args):
    calls.append((name, args))
    return {"ok": True, "result": {"deposit_tnd": args["monthly_rent"] * 2}}


def run(replies, max_steps=6):
    calls.clear()
    model, seen = scripted(replies)
    return fn("run_agent")("Deposit for 900?", model, dispatch, schemas, max_steps=max_steps), seen


happy = ['{"tool": "deposit", "args": {"monthly_rent": 900}}', '{"answer": "1800 TND"}']
check("tool then answer: returns the answer, stopped='answer'", lambda: run(happy)[0]["answer"] == "1800 TND" and run(happy)[0]["stopped"] == "answer")
check("the tool is dispatched with the model's args", lambda: (run(happy), calls)[1] == [("deposit", {"monthly_rent": 900})])
check("the observation is sent back as a user message", lambda: run(happy)[1][1][1][-1] == {"role": "user", "content": "Observation: " + json.dumps({"ok": True, "result": {"deposit_tnd": 1800}})})
check("the system prompt is passed to every call", lambda: all(s == fn("system_prompt")(schemas) for s, _ in run(happy)[1]))
check("steps record type, tool, args, observation", lambda: run(happy)[0]["steps"][0] == {"type": "tool", "tool": "deposit", "args": {"monthly_rent": 900}, "observation": {"ok": True, "result": {"deposit_tnd": 1800}}}
      and run(happy)[0]["steps"][1]["type"] == "answer")
check("messages alternate user / assistant", lambda: [m["role"] for m in run(happy)[0]["messages"]] == ["user", "assistant", "user", "assistant"])
check("an invalid reply gets a correction and the loop continues",
      lambda: (lambda r: r[0]["answer"] == "1800 TND" and r[0]["steps"][0]["type"] == "invalid" and "Invalid reply" in r[1][1][1][-1]["content"])(run(["let me think..."] + happy)))
check("max_steps stops an endless loop", lambda: (lambda r: r[0]["stopped"] == "max_steps" and r[0]["answer"] is None and len(r[1]) == 3)(run(['{"tool": "deposit", "args": {"monthly_rent": 1}}'], max_steps=3)))
