"""The agent loop.

An agent is a simple loop: the model asks for a tool, your code runs it, the result goes
back to the model, and this repeats until the model gives a final answer, or until you
stop it after too many steps.

1. `system_prompt`: tells the model the rules and the tools it can use.
2. `parse_action`: reads each reply (the same as day 29).
3. `run_agent`: the loop itself, with a safety limit on the number of steps.

Running the file uses a **scripted fake model**, so you can follow every step without an
AI key. `run_with_my_model()` runs the same loop with your ⚙ AI model and day 29's tools.
"""
import json
import re


def system_prompt(tool_schemas):
    """The instructions the model gets before the conversation.

    It lists every tool (as JSON, so the model sees names, descriptions and
    argument types) and the **protocol**: reply with exactly one JSON object,
    either a tool call or a final answer. A clear protocol is what lets your
    code understand the model.

    Example:
        >>> schema = {"name": "deposit", "description": "2 months of rent", "input_schema": {}}
        >>> print(system_prompt([schema]))
        You are an assistant for a real estate agency. You can use these tools:
        {"name": "deposit", "description": "2 months of rent", "input_schema": {}}
        <BLANKLINE>
        Reply with ONE JSON object only, each turn:
        {"tool": "<name>", "args": {...}} to call a tool, or
        {"answer": "<final answer for the user>"} when done.
    """
    tools_txt = "\n".join(json.dumps(s, ensure_ascii=False) for s in tool_schemas)
    return ("You are an assistant for a real estate agency. You can use these tools:\n" + tools_txt +
            '\n\nReply with ONE JSON object only, each turn:\n{"tool": "<name>", "args": {...}} to call a tool, or\n'
            '{"answer": "<final answer for the user>"} when done.')


def parse_action(reply):
    """The model's reply as `("tool", name, args)`, `("answer", text)` or `("invalid", reply)`.

    The same function as day 29: find the JSON object in the reply, then look
    for a `"tool"` or an `"answer"` key.

    Example:
        >>> parse_action('{"tool": "deposit", "args": {"monthly_rent": 900}}')
        ('tool', 'deposit', {'monthly_rent': 900})
        >>> parse_action("hmm")
        ('invalid', 'hmm')
    """
    m = re.search(r"\{.*\}", reply, re.S)
    try:
        d = json.loads(m.group())
    except (AttributeError, json.JSONDecodeError):
        return ("invalid", reply)
    if isinstance(d, dict) and "tool" in d:
        return ("tool", d["tool"], d.get("args", {}))
    if isinstance(d, dict) and "answer" in d:
        return ("answer", d["answer"])
    return ("invalid", reply)


def run_agent(task, call_model, dispatch, tool_schemas, max_steps=6):
    """The loop: ask the model, act on its reply, feed the result back, repeat.

    `messages` is the conversation, starting with the user's task. Each step:

    - The model replies, and the reply is added as an `assistant` message.
    - **Answer**: done, return it.
    - **Tool call**: `dispatch` runs it, and the result goes back as a `user`
      message starting with `Observation:`. The model reads it on the next step.
    - **Invalid**: tell the model the correct format and continue.

    `max_steps` is the safety net: a model stuck in a loop is stopped instead of
    spending money forever. `steps` records what happened, for debugging and evals.

    Example (a fake model that calls a tool, then answers):
        >>> replies = iter(['{"tool": "deposit", "args": {"monthly_rent": 900}}',
        ...                 '{"answer": "The deposit is 1800 TND."}'])
        >>> fake_model = lambda system, messages: next(replies)
        >>> fake_dispatch = lambda name, args: {"ok": True, "result": {"deposit_tnd": args["monthly_rent"] * 2}}
        >>> result = run_agent("Deposit for 900?", fake_model, fake_dispatch, [])
        >>> result["answer"], result["stopped"]
        ('The deposit is 1800 TND.', 'answer')
        >>> result["steps"][0]
        {'type': 'tool', 'tool': 'deposit', 'args': {'monthly_rent': 900}, 'observation': {'ok': True, 'result': {'deposit_tnd': 1800}}}
        >>> [m["role"] for m in result["messages"]]
        ['user', 'assistant', 'user', 'assistant']
        >>> stuck = run_agent("?", lambda s, m: "I am thinking...", fake_dispatch, [], max_steps=3)
        >>> stuck["answer"], stuck["stopped"], len(stuck["steps"])
        (None, 'max_steps', 3)
    """
    system = system_prompt(tool_schemas)
    messages, steps = [{"role": "user", "content": task}], []
    for _ in range(max_steps):
        reply = call_model(system, messages)
        messages.append({"role": "assistant", "content": reply})
        action = parse_action(reply)
        if action[0] == "answer":
            steps.append({"type": "answer", "tool": None, "args": None, "observation": None})
            return {"answer": action[1], "stopped": "answer", "steps": steps, "messages": messages}
        if action[0] == "tool":
            obs = dispatch(action[1], action[2])
            steps.append({"type": "tool", "tool": action[1], "args": action[2], "observation": obs})
            messages.append({"role": "user", "content": "Observation: " + json.dumps(obs)})
        else:
            steps.append({"type": "invalid", "tool": None, "args": None, "observation": None})
            messages.append({"role": "user", "content": 'Invalid reply. Answer with ONE JSON object: {"tool": ...} or {"answer": ...}'})
    return {"answer": None, "stopped": "max_steps", "steps": steps, "messages": messages}


def run_with_my_model():
    """The same loop with your real AI model (set in ⚙) and day 29's tools."""
    import sys

    sys.path.append("../day29")
    import tools
    from bench_llm import current_model, get_client

    client = get_client()

    def call_model(system, messages):
        msg = client.messages.create(model=current_model(), max_tokens=300, temperature=0, system=system, messages=messages)
        return msg.content[0].text

    schemas = [tools.tool_schema(n) for n in tools.TOOLS]
    result = run_agent("I want to rent a flat at 900 TND a month and I have a cat. "
                       "How much do I pay up front (agency fee + deposit)?", call_model, tools.dispatch, schemas)
    for s in result["steps"]:
        print(s)
    print("ANSWER:", result["answer"], "| stopped:", result["stopped"])


if __name__ == "__main__":
    # A scripted model that behaves like a real one: one bad reply, two tool calls, then the answer.
    script = iter([
        "I'll look that up for you.",
        '{"tool": "rental_fee", "args": {"monthly_rent": 900}}',
        '{"tool": "deposit", "args": {"monthly_rent": 900, "has_pet": true}}',
        '{"answer": "Up front you pay 900 TND agency fee + 2,250 TND deposit = 3,150 TND."}',
    ])

    def fake_model(system, messages):
        reply = next(script)
        print(f"model says : {reply}")
        return reply

    def agency_tools(name, args):
        rent = args["monthly_rent"]
        result = {"fee_tnd": rent} if name == "rental_fee" else {"deposit_tnd": rent * (2.5 if args.get("has_pet") else 2)}
        print(f"tool result: {result}")
        return {"ok": True, "result": result}

    result = run_agent("I rent at 900 TND a month and have a cat. How much up front?", fake_model, agency_tools, [])
    print("\nsteps:", [s["type"] for s in result["steps"]])
    print("ANSWER:", result["answer"], "| stopped:", result["stopped"])
