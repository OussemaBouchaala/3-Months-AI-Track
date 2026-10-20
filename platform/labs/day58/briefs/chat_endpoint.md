# The chat endpoint
**Topic:** sessions, short history, follow-up questions that still retrieve the right chunks, and routing to the action desk.

## Real example
A help desk bot that remembers the topic for short follow-ups (different domain, same trick):

```python
history = []
def query_for(message):
    last = next((m for role, m in reversed(history) if role == "user"), None)
    return f"{last} {message}" if last and len(message.split()) <= 5 else message
for msg in ["How do I reset my router password?", "and for the wifi one?"]:
    print("search:", query_for(msg))
    history.append(("user", msg))
```

"and for the wifi one?" alone retrieves nothing useful; joined to the previous question, it finds the right page.

## Your mission
Turn `/ask` into a conversation the agent can use all day.

## Steps
1. `route`, `trim_history`, `retrieval_query`.
2. `/chat`: session, route, answer / clarify / confirm / invalid, history.
3. `/chat/confirm` through the day57 desk.
4. Wire the real `answer` (day55 pipeline) and try a 4-message conversation.

## Done when
**Check** passes and a follow-up like "et avec un chat ?" gets the right answer.
