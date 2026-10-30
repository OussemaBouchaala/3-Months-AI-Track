"""`/ask` answers one question. Agents **chat**: "et avec un chat ?" only makes sense after
"combien de caution ?".

`/chat` keeps a short history per session, rewrites short follow-ups for retrieval, and
routes booking requests to day 57's action desk.

1. `route`: is this a question or an action?
2. `trim_history`: keep the last few messages only.
3. `retrieval_query`: make a follow-up searchable on its own.
4. `ChatIn` / `ConfirmIn`: the request bodies.
5. `create_app`: `POST /chat`, `POST /chat/confirm`, `GET /chat/{session_id}`.
"""
import re
import uuid

from fastapi import FastAPI
from pydantic import BaseModel, Field

ACTION_WORDS = re.compile(r"\b(réserver|reserver|book|booking|rdv|rendez-vous)\b|زيارة|نحجز|\bnheb nchouf\b", re.I)
FOLLOWUP_MAX_WORDS = 5


def route(message):
    """`"action"` when the message contains a booking word (French, English,
    Arabic or Derja), else `"question"`.

    A rule is enough today, it's testable and costs nothing. If it misroutes
    too often in your logs, replace it with a small classifier later.

    Example:
        >>> [route(m) for m in ["Je veux réserver une visite", "نحب نحجز زيارة", "nheb nchouf l'appart"]]
        ['action', 'action', 'action']
        >>> route("Can I visit on Sunday?")
        'question'
    """
    return "action" if ACTION_WORDS.search(message) else "question"


def trim_history(history, max_messages=6):
    """Keep only the last `max_messages` messages.

    A long history costs tokens on every call and drags old topics into
    new answers. 6 messages = the last 3 exchanges.

    Example:
        >>> trim_history(list(range(10)), 4)
        [6, 7, 8, 9]
        >>> trim_history([1, 2], 6)
        [1, 2]
    """
    return history[-max_messages:] if max_messages > 0 else []


def retrieval_query(history, message):
    """The text to search the index with.

    "et avec un chat ?" alone finds nothing useful. A short message (at most
    `FOLLOWUP_MAX_WORDS` words) is probably a follow-up, so it's searched
    together with the **last user message**. A long message stands alone.

    `next(..., None)` takes the first match of a generator, or `None`.

    Example:
        >>> H = [{"role": "user", "content": "Combien de caution ?"}, {"role": "assistant", "content": "Deux mois [1]."}]
        >>> retrieval_query(H, "et avec un chat ?")
        'Combien de caution ? et avec un chat ?'
        >>> retrieval_query([], "et un chat ?")
        'et un chat ?'
    """
    last_user = next((m["content"] for m in reversed(history) if m["role"] == "user"), None)
    if last_user and len(message.split()) <= FOLLOWUP_MAX_WORDS:
        return f"{last_user} {message}"
    return message


class ChatIn(BaseModel):
    """A chat message. No `session_id` means "start a new conversation".

    `str | None = None` makes the field optional.

    Example:
        >>> ChatIn(message="Bonjour")
        ChatIn(message='Bonjour', session_id=None)
    """
    message: str = Field(min_length=1, max_length=1000)
    session_id: str | None = None


class ConfirmIn(BaseModel):
    """The agent clicked "Confirmer" on a proposed action.

    Example:
        >>> ConfirmIn(session_id="s1", action_id="abc123").action_id
        'abc123'
    """
    session_id: str
    action_id: str


def create_app(answer, extract_action, desk, max_messages=6):
    """The chat app, around three things you pass in:

    - `answer(query, history)` -> `{"answer", "sources"}` (day 55's pipeline)
    - `extract_action(message)` -> `(tool, args)` or `None` (a model call
      that fills the tool's JSON)
    - `desk`: an `ActionDesk` from day 57

    `POST /chat`:

    1. Use the given `session_id` or create one (`uuid4().hex`).
    2. Question -> `answer(retrieval_query(...), history)`, reply type `answer`.
    3. Action -> no details found: type `clarify` (ask for listing, day,
       time); else `desk.propose`: type `confirm` with the preview and the
       `action_id`, or `invalid` with the errors.
    4. Save the user message and the reply in the session, trimmed.

    `sessions` is a plain dict in memory: enough for one server. With
    several servers you'd put it in Redis or Postgres.

    Example (fakes for the three pieces):
        >>> from fastapi.testclient import TestClient
        >>> class Desk:
        ...     def propose(self, tool, args): return {"status": "needs_confirmation", "action_id": "a1", "preview": "Réserver L12 ?"}
        ...     def confirm(self, aid): return {"status": "done", "result": {"id": 1}}
        >>> app = create_app(lambda q, h: {"answer": f"Réponse à: {q}", "sources": []},
        ...                  lambda m: ("book_visit", {}) if "L12" in m else None, Desk())
        >>> c = TestClient(app)
        >>> r1 = c.post("/chat", json={"message": "Combien de caution ?"}).json()
        >>> r2 = c.post("/chat", json={"message": "et avec un chat ?", "session_id": r1["session_id"]}).json()
        >>> r2["answer"]
        'Réponse à: Combien de caution ? et avec un chat ?'
        >>> c.post("/chat", json={"message": "Je veux réserver le L12"}).json()["type"]
        'confirm'
        >>> c.post("/chat", json={"message": "Je veux réserver"}).json()["answer"]
        'Pour quel bien, quel jour et quelle heure ?'
    """
    app = FastAPI(title="Project chat")
    sessions = {}

    @app.post("/chat")
    def chat(body: ChatIn):
        sid = body.session_id or uuid.uuid4().hex
        history = sessions.get(sid, [])
        if route(body.message) == "question":
            res = answer(retrieval_query(history, body.message), history)
            reply = {"type": "answer", "answer": res["answer"], "sources": res.get("sources", [])}
        else:
            found = extract_action(body.message)
            if found is None:
                reply = {"type": "clarify", "answer": "Pour quel bien, quel jour et quelle heure ?"}
            else:
                p = desk.propose(*found)
                if p["status"] == "needs_confirmation":
                    reply = {"type": "confirm", "answer": p["preview"], "action_id": p["action_id"]}
                else:
                    reply = {"type": "invalid", "answer": "; ".join(p["errors"])}
        history = history + [{"role": "user", "content": body.message}, {"role": "assistant", "content": reply["answer"]}]
        sessions[sid] = trim_history(history, max_messages)
        return {**reply, "session_id": sid}

    @app.post("/chat/confirm")
    def confirm(body: ConfirmIn):
        return desk.confirm(body.action_id)        # the session id is kept for the logs

    @app.get("/chat/{session_id}")
    def history(session_id: str):
        return sessions.get(session_id, [])

    return app


if __name__ == "__main__":
    # Demo: day 57's real ActionDesk with a fake booking system, a fake answer pipeline
    # and a fake extractor. In production: answer = day 55's pipeline, extract_action = a model call.
    import sys
    from fastapi.testclient import TestClient
    sys.path.append("../day57")
    try:
        from action_tool import ActionDesk
        ActionDesk(None).propose("book_visit", {"listing_id": "L1", "when": "2026-12-05T10:00", "client_name": "Am", "phone": "22123456"})["preview"]
    except Exception:                       # day 57 not finished yet: a minimal stand-in desk
        class ActionDesk:
            def __init__(self, execute):
                self.execute = execute
            def propose(self, tool, args):
                return {"status": "needs_confirmation", "action_id": "a1", "preview": f"Réserver une visite du bien {args['listing_id']} ?"}
            def confirm(self, aid):
                return {"status": "done", "result": self.execute("book_visit", {})}

    def answer(query, history):
        if "chat" in query and "caution" in query:
            return {"answer": "Deux mois, plus un demi-mois avec un animal [1][2].", "sources": [{"n": 1}, {"n": 2}]}
        if "caution" in query:
            return {"answer": "Deux mois de loyer [1].", "sources": [{"n": 1}]}
        return {"answer": "I don't know based on the documents.", "sources": []}

    def extract_action(message):
        m = re.search(r"\b(L\d+)\b", message)
        return ("book_visit", {"listing_id": m.group(1), "when": "2026-12-05T10:00", "client_name": "Amel", "phone": "22123456"}) if m else None

    desk = ActionDesk(lambda tool, args: {"visit_id": 42})
    client = TestClient(create_app(answer, extract_action, desk))
    sid = None
    for msg in ["Combien de caution ?", "et avec un chat ?", "Je veux réserver une visite", "Réserver le L12 samedi 10h"]:
        r = client.post("/chat", json={"message": msg, "session_id": sid}).json()
        sid = r["session_id"]
        print(f"agent: {msg}\nbot:   [{r['type']}] {r['answer']}\n")
        if r["type"] == "confirm":
            print("agent clicks Confirmer ->", client.post("/chat/confirm", json={"session_id": sid, "action_id": r["action_id"]}).json(), "\n")
    print("stored history:", len(client.get(f"/chat/{sid}").json()), "messages (trimmed to 6)")
