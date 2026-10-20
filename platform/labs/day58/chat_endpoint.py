# /ask answers one question. Agents chat: "et avec un chat ?" only makes sense after "combien de caution ?".
# /chat keeps a short history per session, rewrites follow-ups for retrieval, and routes actions to the desk.
import re
import uuid

from fastapi import FastAPI
from pydantic import BaseModel, Field

ACTION_WORDS = re.compile(r"\b(réserver|reserver|book|booking|rdv|rendez-vous)\b|زيارة|نحجز|\bnheb nchouf\b", re.I)
FOLLOWUP_MAX_WORDS = 5


def route(message):
    """"action" when ACTION_WORDS matches, else "question". (A rule today; a classifier later if needed.)"""
    # TODO
    ...


def trim_history(history, max_messages=6):
    """Keep only the last max_messages messages (history is a list of {"role", "content"})."""
    # TODO
    ...


def retrieval_query(history, message):
    """Short follow-ups (<= FOLLOWUP_MAX_WORDS words) are searched together with the last USER message:
    "Combien de caution ? et avec un chat ?". Longer messages, or no previous user message: the message alone."""
    # TODO
    ...


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    session_id: str | None = None


class ConfirmIn(BaseModel):
    session_id: str
    action_id: str


def create_app(answer, extract_action, desk, max_messages=6):
    """answer(query, history) -> {"answer", "sources"}; extract_action(message) -> (tool, args) or None;
    desk: an ActionDesk (day57)."""
    app = FastAPI(title="Project chat")
    sessions = {}

    @app.post("/chat")
    def chat(body: ChatIn):
        """1. session_id: the given one, or a new uuid4 hex. 2. history = that session's messages.
        3. route(message):
           - "question": answer(retrieval_query(history, message), history) -> reply {"type": "answer", "answer", "sources"}
           - "action": extract_action(message); None -> {"type": "clarify", "answer": "Pour quel bien, quel jour et quelle heure ?"};
             else desk.propose(tool, args) -> {"type": "confirm", "answer": preview, "action_id"} or
             {"type": "invalid", "answer": "; ".join(errors)}
        4. Append the user message and {"role": "assistant", "content": reply["answer"]}; trim to max_messages.
        Return the reply plus "session_id"."""
        # TODO
        ...

    @app.post("/chat/confirm")
    def confirm(body: ConfirmIn):
        """desk.confirm(action_id), returned as is. (The session id is kept for the logs.)"""
        # TODO
        ...

    @app.get("/chat/{session_id}")
    def history(session_id: str):
        return sessions.get(session_id, [])

    return app


if __name__ == "__main__":
    print("Wire it like day55: answer = the /ask pipeline, extract_action = a model call that returns the tool JSON,")
    print("desk = ActionDesk(execute) from day57. Then: uvicorn chat_endpoint:app --reload")
