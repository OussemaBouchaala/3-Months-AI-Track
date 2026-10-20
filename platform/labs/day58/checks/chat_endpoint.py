from fastapi.testclient import TestClient
rt = fn("route")
check("route: action words in FR, EN, Arabic, Derja", lambda: all(rt(m) == "action" for m in ["Je veux réserver une visite", "book L12 saturday", "نحب نحجز زيارة", "nheb nchouf l'appart"]))
check("route: questions stay questions", lambda: all(rt(m) == "question" for m in ["Combien de caution ?", "Can I visit on Sunday?", "شنية الوثائق؟"]))
th = fn("trim_history")
check("trim_history keeps the last messages", lambda: th(list(range(10)), 4) == [6, 7, 8, 9] and th([1, 2], 6) == [1, 2])
rq = fn("retrieval_query")
H = [{"role": "user", "content": "Combien de caution ?"}, {"role": "assistant", "content": "Deux mois [1]."}]
check("short follow-up is joined to the last user message", lambda: rq(H, "et avec un chat ?") == "Combien de caution ? et avec un chat ?")
check("long message or empty history: unchanged", lambda: rq(H, "Quels documents faut-il pour louer un appartement à Sousse ?") == "Quels documents faut-il pour louer un appartement à Sousse ?" and rq([], "et un chat ?") == "et un chat ?")
seen = []
def answer(query, history):
    seen.append((query, len(history)))
    return {"answer": f"Réponse à: {query}", "sources": [{"n": 1}]}
def extract(msg):
    return ("book_visit", {"listing_id": "L12"}) if "L12" in msg else None
class Desk:
    def __init__(self):
        self.confirmed = []
    def propose(self, tool, args):
        return {"status": "needs_confirmation", "action_id": "abc123", "preview": "Réserver L12 ?"} if args.get("listing_id") == "L12" else {"status": "invalid", "errors": ["x"]}
    def confirm(self, aid):
        self.confirmed.append(aid)
        return {"status": "done", "result": {"id": 1}}
create_app = fn("create_app")
def _client():
    d = Desk()
    return TestClient(create_app(answer, extract, d, max_messages=4)), d
def _q():
    c, _ = _client()
    seen.clear()
    r1 = c.post("/chat", json={"message": "Combien de caution ?"}).json()
    r2 = c.post("/chat", json={"message": "et avec un chat ?", "session_id": r1["session_id"]}).json()
    return r1, r2
check("a question gets an answer and a new session id", lambda: (lambda r: r[0]["type"] == "answer" and len(r[0]["session_id"]) == 32 and r[0]["sources"] == [{"n": 1}])(_q()))
check("the follow-up is searched with the previous question and the history", lambda: (_q(), seen[1])[1] == ("Combien de caution ? et avec un chat ?", 2))
def _hist():
    c, _ = _client()
    sid = c.post("/chat", json={"message": "a ?"}).json()["session_id"]
    for m in ["b ?", "c ?"]:
        c.post("/chat", json={"message": m, "session_id": sid})
    h = c.get(f"/chat/{sid}").json()
    return len(h) == 4 and h[0] == {"role": "user", "content": "b ?"}
check("history is stored per session and trimmed", _hist)
def _action():
    c, d = _client()
    r = c.post("/chat", json={"message": "Réserver une visite du L12 samedi 10h"}).json()
    r2 = c.post("/chat/confirm", json={"session_id": r["session_id"], "action_id": r["action_id"]}).json()
    return r["type"] == "confirm" and r["answer"] == "Réserver L12 ?" and r2["status"] == "done" and d.confirmed == ["abc123"]
check("an action is proposed, then confirmed through /chat/confirm", _action)
check("an action without details asks to clarify", lambda: _client()[0].post("/chat", json={"message": "je veux réserver"}).json()["type"] == "clarify")
