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

## Your mission
Write the post you'll publish with your demo video.

## Steps
1. Hook line with a number or a surprising fact.
2. What, for whom, how well (3+ numbers from results.md).
3. One thing that failed and what you learned. It's the part people comment on.
4. GitHub link, 1-5 hashtags, no Markdown.
5. Publish it the same day as the video. Reply to every comment in the first hour.

## Done when
**Check** passes and the post is published.
