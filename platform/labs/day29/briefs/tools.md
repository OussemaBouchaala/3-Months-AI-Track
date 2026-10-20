# Tools the model can request
**Topic:** a schema describes the tool; dispatch validates the request and never trusts it.

## Real example
A smart-home assistant exposes two tools. A request from the model is just JSON: the code checks the name and the arguments before anything happens.

```python
import json
from pydantic import BaseModel, ValidationError

class LightArgs(BaseModel):
    room: str
    on: bool

registry = {"set_light": (lambda room, on: f"{room} light {'on' if on else 'off'}", LightArgs)}

def dispatch(name, args):
    if name not in registry:
        return {"ok": False, "error": f"unknown tool: {name}"}
    fn, model = registry[name]
    try:
        return {"ok": True, "result": fn(**model.model_validate(args).model_dump())}
    except ValidationError as e:
        return {"ok": False, "error": "invalid arguments: " + e.errors()[0]["msg"]}

for request in ['{"tool": "set_light", "args": {"room": "kitchen", "on": true}}',
                '{"tool": "set_light", "args": {"room": "kitchen", "on": "maybe"}}',
                '{"tool": "unlock_front_door", "args": {}}']:
    r = json.loads(request)
    print(dispatch(r["tool"], r["args"]))
print(json.dumps(LightArgs.model_json_schema()))
```

## Your mission
Build the tool registry, schemas, a safe dispatcher, and the action parser.

## Steps
1. `tool`: a decorator factory (a function returning a decorator) that fills `TOOLS`.
2. `tool_schema`: name, description, `input_schema`.
3. `dispatch`: unknown → validate → call, each failure becomes `{"ok": False, "error": ...}`.
4. `parse_action`: regex the `{...}`, `json.loads`, check the keys.
5. `deposit`: 2 months + 0.5 with a pet (from the handbook).

## Done when
**Check** passes; Run shows 4 replies handled without a crash.
