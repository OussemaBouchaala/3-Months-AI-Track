# Architecture on one page
**Topic:** components, one diagram, the path of one question, and the decisions you'd defend in an interview.

## Real example
Mermaid is text that renders as a diagram on GitHub. A different system (a parking app) in 6 lines:

```python
diagram = """flowchart LR
    App[Mobile app] --> API[FastAPI]
    API --> DB[(Postgres)]
    API --> Pay[Payment provider]
    Cam[Gate camera] --> OCR[Plate OCR]
    OCR --> API"""
print(diagram)
print("arrows:", diagram.count("-->"))
```

`[(...)]` draws a database cylinder, `[...]` a box. Paste it into [mermaid.live](https://mermaid.live) to see it.

## Your mission
Describe the system you'll build in Weeks 8-11, before writing its code.

## Steps
1. List the components (reuse Phase 1: normalizer, chunker, hybrid search, agent tools).
2. Draw the Mermaid flowchart (at least 5 arrows), outside the comment.
3. Write the data flow of one real question from your interview.
4. Two decisions written as "X instead of Y, because Z", and two risks.

## Done when
**Check** passes and the diagram renders on [mermaid.live](https://mermaid.live).
