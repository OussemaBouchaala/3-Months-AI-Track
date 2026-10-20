# Stream the answer
**Topic:** Server-Sent Events: the format, a generator that emits tokens, sources and done, and the browser side.

## Real example
A progress feed for a long file conversion (different stream, same format):

```python
def sse(data, event=None):
    return (f"event: {event}\n" if event else "") + "".join(f"data: {l}\n" for l in str(data).split("\n")) + "\n"
feed = "".join([sse("10%", "progress"), sse("60%", "progress"), sse("report.pdf", "done")])
print(feed)
print([b.split("\n")[0] for b in feed.strip().split("\n\n")])
```

The format is just text: `field: value` lines, a blank line between events. Any HTTP client can read it, and browsers have `EventSource` built in.

## Your mission
Make answers appear word by word, with sources at the end.

## Steps
1. `sse_event` and `parse_sse` (you'll use the same logic in JavaScript tomorrow).
2. `stream_answer`: tokens, sources, done; an error event if generation fails.
3. `/stream` with the right media type and headers.
4. **Run**, then open the URL printed in the browser and watch it arrive.

## Done when
**Check** passes and the browser shows the answer arriving word by word.
