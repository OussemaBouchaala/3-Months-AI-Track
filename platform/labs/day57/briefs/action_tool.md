# The real action, done safely
**Topic:** propose, preview in plain language, confirm once, expire, audit. The model never presses the button.

## Real example
A bank transfer screen works the same way (different action, same steps):

```python
import hashlib, json
pending, done = {}, {}
def propose(to, amount):
    aid = hashlib.sha256(json.dumps({"to": to, "amount": amount}, sort_keys=True).encode()).hexdigest()[:8]
    pending[aid] = (to, amount)
    return aid, f"Send {amount} TND to {to}?"
def confirm(aid):
    if aid in done: return "already sent"
    to, amount = pending.pop(aid)
    done[aid] = True
    return f"sent {amount} TND to {to}"
aid, text = propose("Sami", 150)
print(text); print(confirm(aid)); print(confirm(aid))
```

The double-click doesn't send twice, and nothing is sent until a human reads the sentence and says yes.

## Your mission
Write the action layer for your project's tool (book_visit here; adapt the args model to yours).

## Steps
1. `action_id` and `preview`.
2. `ActionDesk.propose`: unknown tool, Pydantic errors, pending with time.
3. `confirm`: already done, unknown, expired, failed (stays pending), done. And `cancel`.
4. Start the day31 visits API on port 8001, then **Run**: confirm twice, see one booking.

## Done when
**Check** passes and the real API shows one visit after two confirmations.
