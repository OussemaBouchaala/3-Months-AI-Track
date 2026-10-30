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

## How to read this example
An example one-page architecture for the agency assistant. Notice how it's built:

1. **Components** reuse Phase 1: normalizer, chunker, hybrid search, agent tools.
2. **The Mermaid diagram** (paste it into [mermaid.live](https://mermaid.live) to see it drawn).
3. **The path of one real question**, step by step, from the user to the answer.
4. **Decisions** written as "X instead of Y, because Z", and **risks** with what you'd do about them. These are the parts an interviewer asks about.

Press **Check** under the editor to see the rules a good version follows. When you write your own, keep this structure and use your real numbers.
