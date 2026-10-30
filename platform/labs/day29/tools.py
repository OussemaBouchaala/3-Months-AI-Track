"""Tools: Python functions a model is allowed to call.

An LLM never runs code itself. It **writes a request** ("call `deposit` with rent 900"),
and **your code** checks that request and decides whether to run it. That's what makes
agents safe enough to use.

1. `tool`: a decorator that registers a function in the `TOOLS` registry.
2. `tool_schema`: describes a tool to the model (name, description, JSON schema of its arguments).
3. `dispatch`: the only door to the tools. It validates the arguments and catches every error.
4. `parse_action`: reads the model's reply: a tool call, a final answer, or garbage.
5. Two real tools for the agency: `rental_fee` and `deposit`.
"""
import json
import re

from pydantic import BaseModel, ValidationError

TOOLS = {}   # name -> {"fn": function, "args": pydantic model, "description": str}


def tool(name, description, args_model):
    """A decorator that registers a function as a tool.

    Writing `@tool("deposit", "...", DepositArgs)` above a function stores it in
    `TOOLS` together with its description and the Pydantic model that describes
    its arguments. The function itself is returned **unchanged**, so you can
    still call it normally.

    `tool(...)` returns `decorator`, and Python calls `decorator(f)` with the
    function defined below the `@` line (a decorator with arguments needs this
    extra level).

    Example:
        >>> class EchoArgs(BaseModel):
        ...     text: str
        >>> @tool("echo", "Repeat the text", EchoArgs)
        ... def echo(text):
        ...     return text
        >>> "echo" in TOOLS, TOOLS["echo"]["description"]
        (True, 'Repeat the text')
        >>> echo("still a normal function")
        'still a normal function'
    """
    def decorator(f):
        TOOLS[name] = {"fn": f, "args": args_model, "description": description}
        return f
    return decorator


def tool_schema(name):
    """The tool described the way an LLM API expects it.

    The model reads this to know what the tool does and which arguments it takes.
    `model_json_schema()` turns the Pydantic model into a standard JSON Schema:
    argument names, types, which ones are required, and defaults.

    Example:
        >>> schema = tool_schema("deposit")
        >>> schema["name"], schema["description"]
        ('deposit', 'Security deposit for a yearly rental: 2 months, +0.5 month with a pet.')
        >>> schema["input_schema"]["properties"]["monthly_rent"]
        {'title': 'Monthly Rent', 'type': 'number'}
        >>> schema["input_schema"]["required"]
        ['monthly_rent']
    """
    t = TOOLS[name]
    return {"name": name, "description": t["description"], "input_schema": t["args"].model_json_schema()}


def dispatch(name, args):
    """Run a tool safely and always return a dict the model can read.

    Three things can go wrong, and none of them may crash your app:

    1. The model asks for a tool that doesn't exist: refused.
    2. The arguments are wrong (a word where a number should be): the Pydantic
       model rejects them with `ValidationError`.
    3. The tool itself raises an error: caught and reported.

    The error goes back to the model as text, so it can fix its request and try again.

    Example:
        >>> dispatch("deposit", {"monthly_rent": 900, "has_pet": True})
        {'ok': True, 'result': {'deposit_tnd': 2250.0}}
        >>> dispatch("delete_database", {})
        {'ok': False, 'error': 'unknown tool: delete_database'}
        >>> dispatch("deposit", {"monthly_rent": "cheap"})["error"]
        'invalid arguments: Input should be a valid number, unable to parse string as a number'
    """
    if name not in TOOLS:
        return {"ok": False, "error": f"unknown tool: {name}"}
    t = TOOLS[name]
    try:
        valid = t["args"].model_validate(args)
    except ValidationError as e:
        return {"ok": False, "error": "invalid arguments: " + e.errors()[0]["msg"]}
    try:
        return {"ok": True, "result": t["fn"](**valid.model_dump())}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


def parse_action(reply):
    """Read the model's reply: a tool call, a final answer, or something invalid.

    Models often add text around the JSON ("Sure! {...}"), so
    `re.search(r"\\{.*\\}", reply, re.S)` finds the part from the first `{` to
    the last `}` (`re.S` lets `.` match line breaks too). If there is no JSON,
    or it is broken, or it has neither key, the reply is `"invalid"`.

    Example:
        >>> parse_action('Sure! {"tool": "deposit", "args": {"monthly_rent": 900}}')
        ('tool', 'deposit', {'monthly_rent': 900})
        >>> parse_action('{"answer": "The deposit is 1,800 TND."}')
        ('answer', 'The deposit is 1,800 TND.')
        >>> parse_action("Let me think about it...")
        ('invalid', 'Let me think about it...')
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


# --- Two real tools for the agency ---------------------------------------------------------

class FeeArgs(BaseModel):
    """The arguments of `rental_fee`: one number, the monthly rent in TND.

    Pydantic converts and checks the input: `"900"` becomes `900.0`, `"cheap"` is refused.

    Example:
        >>> FeeArgs(monthly_rent="900")
        FeeArgs(monthly_rent=900.0)
    """
    monthly_rent: float


@tool("rental_fee", "Agency fee the tenant pays for a yearly rental (one month of rent).", FeeArgs)
def rental_fee(monthly_rent):
    """The agency fee for a yearly rental: one month of rent.

    Example:
        >>> rental_fee(900)
        {'fee_tnd': 900}
    """
    return {"fee_tnd": monthly_rent}


class DepositArgs(BaseModel):
    """The arguments of `deposit`. `has_pet` is optional and defaults to `False`.

    Example:
        >>> DepositArgs(monthly_rent=900)
        DepositArgs(monthly_rent=900.0, has_pet=False)
    """
    monthly_rent: float
    has_pet: bool = False


@tool("deposit", "Security deposit for a yearly rental: 2 months, +0.5 month with a pet.", DepositArgs)
def deposit(monthly_rent, has_pet=False):
    """The security deposit: 2 months of rent, or 2.5 months with a pet.

    Example:
        >>> deposit(900)
        {'deposit_tnd': 1800}
        >>> deposit(900, has_pet=True)
        {'deposit_tnd': 2250.0}
    """
    return {"deposit_tnd": monthly_rent * (2.5 if has_pet else 2)}


if __name__ == "__main__":
    print("What the model sees:")
    print(json.dumps([tool_schema(n) for n in TOOLS], indent=1))
    print("\nFour replies a model might write, and what your code does with each:")
    for reply in ['{"tool": "deposit", "args": {"monthly_rent": 900, "has_pet": true}}',
                  'Sure! {"tool": "deposit", "args": {"monthly_rent": "cheap"}}',
                  '{"tool": "delete_database", "args": {}}',
                  '{"answer": "The deposit is 2,250 TND."}']:
        action = parse_action(reply)
        print(action[0], "->", dispatch(action[1], action[2]) if action[0] == "tool" else action[1])
