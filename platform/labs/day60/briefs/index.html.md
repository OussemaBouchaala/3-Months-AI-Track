# A usable web page
**Topic:** one HTML file, no framework: chat log, right-to-left aware, sources, confirm button, safe rendering.

## Real example
Why `textContent` and not `innerHTML` (a different page, the same danger). A model answer can contain anything, including HTML that runs code:

```python
import html
answer = 'Deux mois <img src=x onerror="alert(document.cookie)">'
print("innerHTML would render a tag and RUN the onerror script")
print("textContent shows it as text:", html.escape(answer))
```

The agent pastes a client's message, the model repeats part of it, and the page executes it. `textContent` makes that impossible.

## How to read this page
The file in the editor is the complete chat page the agent uses, served by the day 58 chat service. Read it top to bottom; the comments explain each part:

1. **The head**: `charset="utf-8"` for Arabic, the `viewport` line for phones, a little CSS for the bubbles.
2. **The form**: `textarea#message` with `dir="auto"`, so Arabic goes right-to-left and French left-to-right on their own.
3. **`addMessage`**: every bubble is filled with `textContent`, never as HTML.
4. **`postJSON`**: one helper for every call; an HTTP error throws, so each caller has one `catch`.
5. **The submit handler**: show the message, POST `/chat` with the session id, show the answer and its sources, and re-enable the button in `finally`.
6. **`addConfirm`**: for `type === "confirm"`, a button that POSTs `/chat/confirm` once.

## See it working
In `../day58/chat_endpoint.py`, add `from fastapi.responses import FileResponse` and a route `@app.get("/")` returning `FileResponse("../day60/index.html")`, start the service, and open http://127.0.0.1:8000/. Ask in French, follow up in Arabic, then book a visit.

Press **Check** under the editor to see the rules a safe chat page follows.
