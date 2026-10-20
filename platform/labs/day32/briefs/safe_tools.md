# Guardrails for actions
**Topic:** retries for flaky errors, confirmation for writes, idempotency against doubles, documents as data.

## Real example
A payment bot. The network times out once; the retry must not charge the card twice. The idempotency key makes the second attempt a no-op:

```python
import hashlib, json

charged = set()

def key(name, args):
    return hashlib.sha256((name + json.dumps(args, sort_keys=True)).encode()).hexdigest()[:16]

def charge(args):
    k = key("charge", args)
    if k in charged:
        return {"ok": True, "result": "already charged, nothing done"}
    charged.add(k)
    return {"ok": True, "result": f"charged {args['amount']} TND"}

print(charge({"card": "1234", "amount": 150}))
print(charge({"amount": 150, "card": "1234"}))   # retry after a timeout, keys in another order
```

## Your mission
Wrap tool calls so an agent can act safely on your visits API.

## Steps
1. `api_call`: map 2xx / 4xx / 5xx / timeout to observations (`retryable` only for 5xx and timeouts).
2. `with_retry`: loop up to `attempts`, stop early if not retryable.
3. `idempotency_key` (sorted keys), `confirm_gate`, `already_done`.
4. `as_untrusted`: strip the tags from the text, then wrap it.
5. With the day31 API running, **Run**.

## Done when
**Check** passes: no double bookings, no write without confirmation, no retry on a 422.
