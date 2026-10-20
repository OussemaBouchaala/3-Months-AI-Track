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

## Your mission
Write the page the agent will use, served by the day58 chat service.

## Steps
1. The form: `textarea#message` with `dir="auto"`, `button#send`.
2. `addMessage` with `textContent` and `dir = "auto"`.
3. Submit: POST `/chat` with the session id, show answer and sources, handle errors, `finally` re-enable.
4. The confirm button for `type === "confirm"`.
5. Serve it: in `chat_endpoint.py` add `from fastapi.responses import FileResponse` and a `GET /` route returning `FileResponse("../day60/index.html")`. Open http://127.0.0.1:8000/.

## Done when
**Check** passes and you can ask, follow up, and confirm a booking from the browser, in Arabic and French.
