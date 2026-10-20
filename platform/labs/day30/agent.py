# The agent loop: the model asks for a tool, your code runs it, the result goes back, repeat until an answer.
# Check drives the loop with a scripted fake model. Run uses your ⚙ AI model and Monday's tools.
import json
import re


def system_prompt(tool_schemas):
    """Tell the model the protocol and the tools. It must contain:
    - every tool's name, description and input_schema (json.dumps each schema)
    - the two reply formats, as JSON only, one per turn:
        {"tool": "<name>", "args": {...}}      to call a tool
        {"answer": "<final answer for the user>"}   when done"""
    # TODO
    ...


def parse_action(reply):
    """Same as Monday: ("tool", name, args) | ("answer", text) | ("invalid", reply)."""
    # TODO (copy yours from day29)
    ...


def run_agent(task, call_model, dispatch, tool_schemas, max_steps=6):
    """call_model(system, messages) -> reply text. dispatch(name, args) -> observation dict.
    messages starts as [{"role": "user", "content": task}].
    Each step:
      reply = call_model(...); append {"role": "assistant", "content": reply}
      answer  -> stop, stopped = "answer"
      tool    -> obs = dispatch(name, args); append {"role": "user", "content": "Observation: " + json.dumps(obs)}
      invalid -> append {"role": "user", "content": 'Invalid reply. Answer with ONE JSON object: {"tool": ...} or {"answer": ...}'}
    Stop with stopped = "max_steps" after max_steps model calls.
    Return {"answer": text or None, "stopped": ..., "steps": [one dict per step:
            {"type": "tool"/"answer"/"invalid", "tool": name or None, "args": args or None, "observation": obs or None}],
            "messages": messages}"""
    # TODO
    ...


if __name__ == "__main__":
    import sys

    sys.path.append("../day29")
    import tools   # Monday's registry: rental_fee and deposit
    from bench_llm import get_client, current_model

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
