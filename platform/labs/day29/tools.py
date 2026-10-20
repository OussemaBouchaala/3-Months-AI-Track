# Tools: Python functions a model may call, described by JSON schemas, called only through dispatch().
# The model never runs code. It writes a request; YOUR code validates it and decides.
import json
import re

from pydantic import BaseModel, ValidationError

TOOLS = {}   # name -> {"fn": function, "args": pydantic model, "description": str}


def tool(name, description, args_model):
    """Decorator that registers a function in TOOLS (Week 1 Day 3: decorators).
        @tool("get_fee", "Agency fee for a rental", FeeArgs)
        def get_fee(monthly_rent): ...
    Store {"fn": f, "args": args_model, "description": description} under name, return f unchanged."""
    def decorator(f):
        # TODO: register f in TOOLS
        return f
    return decorator


def tool_schema(name):
    """The tool as an LLM API expects it (Anthropic format):
    {"name": name, "description": ..., "input_schema": args_model.model_json_schema()}"""
    # TODO
    ...


def dispatch(name, args):
    """Run a tool safely. Return a dict the model will read as an observation:
      unknown name           -> {"ok": False, "error": "unknown tool: <name>"}
      args fail validation   -> {"ok": False, "error": "invalid arguments: <short message>"}
      the tool raises        -> {"ok": False, "error": "<ExceptionName>: <message>"}
      success                -> {"ok": True, "result": <return value>}
    Validate with the args model, then call fn(**validated.model_dump())."""
    # TODO
    ...


def parse_action(reply):
    """The model replies with ONE JSON object, maybe with text around it:
        {"tool": "<name>", "args": {...}}   -> ("tool", name, args)
        {"answer": "<text>"}                 -> ("answer", text)
    Anything else (no JSON, bad JSON, other keys) -> ("invalid", reply).
    Find the object with re.search(r"\{.*\}", reply, re.S)."""
    # TODO
    ...


# --- Two real tools for the agency ---------------------------------------------------------

class FeeArgs(BaseModel):
    monthly_rent: float


@tool("rental_fee", "Agency fee the tenant pays for a yearly rental (one month of rent).", FeeArgs)
def rental_fee(monthly_rent):
    return {"fee_tnd": monthly_rent}


class DepositArgs(BaseModel):
    monthly_rent: float
    has_pet: bool = False


@tool("deposit", "Security deposit for a yearly rental: 2 months, +0.5 month with a pet.", DepositArgs)
def deposit(monthly_rent, has_pet=False):
    # TODO: 2 months of rent, plus half a month if has_pet. Return {"deposit_tnd": amount}
    ...


if __name__ == "__main__":
    print(json.dumps([tool_schema(n) for n in TOOLS], indent=1))
    for reply in ['{"tool": "deposit", "args": {"monthly_rent": 900, "has_pet": true}}',
                  'Sure! {"tool": "deposit", "args": {"monthly_rent": "cheap"}}',
                  '{"tool": "delete_database", "args": {}}',
                  '{"answer": "The deposit is 2,250 TND."}']:
        action = parse_action(reply)
        print(action[0], "->", dispatch(action[1], action[2]) if action[0] == "tool" else action[1])
