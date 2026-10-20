from fastapi.testclient import TestClient

bp = fn("build_prompt")
CH = [{"id": "reg-c0", "doc_id": "reg", "title": "Règlement", "section": "Caution", "text": "Deux mois de loyer."},
      {"id": "faq-c3", "doc_id": "faq", "title": "FAQ", "section": "", "text": "Un demi-mois en plus avec un animal."}]
check("build_prompt numbers the sources with title > section", lambda: "[1] Règlement > Caution\nDeux mois de loyer." in bp("Caution ?", CH) and "[2] FAQ\nUn demi-mois" in bp("Caution ?", CH))
check("build_prompt contains the IDK sentence and the question", lambda: var("IDK") in bp("Caution ?", CH) and "Caution ?" in bp("Caution ?", CH))
create_app = fn("create_app")
calls = {"gen": 0, "q": None}
def retrieve(q, k):
    calls["q"] = q
    return [] if "voiture" in q else CH[:k]
def generate(prompt):
    calls["gen"] += 1
    if "PANNE" in prompt:
        raise RuntimeError("ollama down")
    return "La caution est de deux mois [1, 7]. Plus un demi-mois avec un chat [2]." if "[2]" in prompt else "Deux mois [1]."
client = lambda: TestClient(create_app(retrieve, generate, scrub=lambda t: t.replace("98123456", "[PHONE_1]")))
ask = lambda **b: client().post("/ask", json={"question": "Combien de caution ?", **b})
check("GET /health -> ok", lambda: client().get("/health").json() == {"status": "ok"})
check("POST /ask returns answer, idk, sources, latency_ms", lambda: set(ask().json()) >= {"answer", "idk", "sources", "latency_ms"} and ask().json()["idk"] is False)
check("invalid citation markers are removed, sources follow citation order", lambda: (lambda r: "[7]" not in r["answer"] and [s["id"] for s in r["sources"]] == ["reg-c0", "faq-c3"] and r["sources"][0]["n"] == 1)(ask().json()))
check("k is passed to the retriever", lambda: [s["n"] for s in ask(k=1).json()["sources"]] == [1])
check("no chunks -> IDK without calling the model", lambda: (calls.update(gen=0), ask(question="Vous vendez une voiture ?").json())[1]["idk"] is True and calls["gen"] == 0)
check("the question is scrubbed before retrieval", lambda: (ask(question="Rappelez le 98123456 svp"), calls["q"])[1] == "Rappelez le [PHONE_1] svp")
check("model failure -> 503", lambda: ask(question="PANNE totale ?").status_code == 503)
check("validation: empty question and k=50 -> 422", lambda: ask(question="").status_code == 422 and ask(k=50).status_code == 422)
check("X-Request-ID is echoed, or created", lambda: client().get("/health", headers={"X-Request-ID": "abc"}).headers.get("x-request-id") == "abc" and len(client().get("/health").headers.get("x-request-id", "")) == 32)
