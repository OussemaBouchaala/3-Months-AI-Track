# The agent loop
**Topic:** an agent is a loop: model → action → observation → model, with a hard step limit.

## Real example
A travel assistant answers "Is it warmer in Tunis or Paris?" by calling a weather tool twice, then answering. The "model" is a script of replies, so you can watch the loop itself:

```python
import json

script = iter(['{"tool": "weather", "args": {"city": "Tunis"}}',
               '{"tool": "weather", "args": {"city": "Paris"}}',
               '{"answer": "Tunis is warmer: 24°C vs 13°C."}'])
weather = {"Tunis": 24, "Paris": 13}
messages = [{"role": "user", "content": "Is it warmer in Tunis or Paris?"}]

for step in range(5):                       # hard limit: never loop forever
    reply = json.loads(next(script))
    messages.append({"role": "assistant", "content": json.dumps(reply)})
    if "answer" in reply:
        print("ANSWER:", reply["answer"]); break
    obs = {"ok": True, "result": weather[reply["args"]["city"]]}
    messages.append({"role": "user", "content": "Observation: " + json.dumps(obs)})
    print(step, reply["tool"], reply["args"], "->", obs)
```

## Your mission
Write the loop that lets a model use Monday's tools to answer a 2-step question.

## Steps
1. `system_prompt`: the protocol + every schema.
2. `parse_action`: copy Monday's.
3. `run_agent`: loop up to `max_steps`; handle answer / tool / invalid; record each step.
4. **Run**: the model should call `rental_fee` and `deposit`, then answer 900 + 2,250 = 3,150 TND.

## Done when
**Check** passes, and the trace shows two tool calls and a correct total.
