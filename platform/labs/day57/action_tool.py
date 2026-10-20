# The project's real action, done safely: the model PROPOSES, the agent sees a plain-language preview and
# CONFIRMS, and only then does it run, exactly once, with an audit trail. (Week 5's guardrails, made concrete.)
import hashlib
import json
from datetime import datetime, timedelta

from pydantic import BaseModel, Field, ValidationError

CONFIRM_TTL = timedelta(minutes=10)
DAYS_FR = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


class BookVisitArgs(BaseModel):
    listing_id: str = Field(pattern=r"^L\d{1,5}$")
    when: datetime
    client_name: str = Field(min_length=2, max_length=80)
    phone: str = Field(pattern=r"^\+?\d{8,12}$")


TOOLS = {"book_visit": BookVisitArgs}


def action_id(tool, args):
    """Same tool + same arguments -> same id: first 16 hex of sha256 of json.dumps({"tool", "args"}, sort_keys=True,
    default=str). Asking twice for the same booking gives the same pending action, not two."""
    # TODO
    ...


def preview(tool, args):
    """The sentence the agent confirms, in French. For book_visit:
    "Réserver une visite du bien L12 le samedi 05/12 à 10:00 pour Amel (22123456)." (args is a BookVisitArgs)."""
    # TODO
    ...


class ActionDesk:
    """Pending actions waiting for a human yes. execute(tool, args_dict) does the real work (an API call)."""

    def __init__(self, execute, now=datetime.now):
        self.execute, self.now = execute, now
        self.pending, self.done, self.audit = {}, {}, []

    def _log(self, aid, tool, status):
        self.audit.append({"at": self.now().isoformat(timespec="seconds"), "action_id": aid, "tool": tool, "status": status})

    def propose(self, tool, raw_args):
        """Unknown tool -> {"status": "invalid", "errors": ["unknown tool"]}. Invalid args -> "invalid" with one error
        string per Pydantic error ("<field>: <msg>"). Otherwise store it as pending with its creation time and return
        {"status": "needs_confirmation", "action_id", "preview"}. Log "proposed" or "invalid" to the audit."""
        # TODO
        ...

    def confirm(self, aid):
        """Already done -> {"status": "already_done", "result": <same result>} (no second execution).
        Not pending -> {"status": "unknown"}. Older than CONFIRM_TTL -> drop it, {"status": "expired"}.
        Otherwise execute(tool, args.model_dump(mode="json")); success -> {"status": "done", "result": ...};
        an exception -> {"status": "failed", "error": str(e)} and the action stays pending (can be retried).
        Log every outcome."""
        # TODO
        ...

    def cancel(self, aid):
        """Remove a pending action. True if it was pending."""
        # TODO
        ...


if __name__ == "__main__":
    import httpx
    # The day31 visits API must be running: uvicorn visits_api:app --port 8001 (in ../day31)
    execute = lambda tool, args: httpx.post("http://127.0.0.1:8001/visits", json={
        "name": args["client_name"], "phone": args["phone"], "listing_ids": [args["listing_id"]], "when": args["when"]}, timeout=10).raise_for_status().json()
    desk = ActionDesk(execute)
    p = desk.propose("book_visit", {"listing_id": "L12", "when": "2026-12-05T10:00", "client_name": "Amel", "phone": "22123456"})
    print(p)
    if p["status"] == "needs_confirmation" and input("Confirmer ? (o/n) ") == "o":
        print(desk.confirm(p["action_id"]))
        print(desk.confirm(p["action_id"]))         # second click: no double booking
    print(json.dumps(desk.audit, indent=1))
