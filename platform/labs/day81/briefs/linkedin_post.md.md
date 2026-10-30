# The LinkedIn post
**Topic:** a short post with a hook, real numbers, one honest lesson, and the link. Written for people who scroll.

## Real example
Two first lines for the same project (a different project: a bus-arrival predictor in Tunis):

```python
hooks = ["I'm excited to announce that I have completed my machine learning project!",
         "The 32 bus in Tunis is late 41% of the time. I built a model that predicts by how much."]
for h in hooks:
    print(len(h), "chars |", "number" if any(c.isdigit() for c in h) else "no number", "|", h)
```

LinkedIn shows about two lines before "...see more". The second hook earns the click; the first one gets scrolled past.

## How to read this example
An example LinkedIn post to publish with the demo video. Notice how it's built:

1. **The hook line** has a number or a surprising fact: it's all most people read.
2. **What, for whom, how well**: three or more real numbers.
3. **One honest failure** and the lesson. It's the part people comment on.
4. **The link and a few hashtags**, no Markdown (LinkedIn doesn't render it).

Press **Check** under the editor to see the rules a good version follows. When you write your own, keep this structure and use your real numbers.
