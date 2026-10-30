"""The project's real action, done safely.

The model **proposes**, the agent sees a plain-language preview and **confirms**, and only
then does it run, **exactly once**, with an audit trail. Week 5's guardrails, made concrete.

1. `BookVisitArgs`: the arguments, validated (a model can invent anything).
2. `action_id`: the same request always gets the same id.
3. `preview`: the French sentence the agent says yes to.
4. `ActionDesk`: propose, confirm, cancel; pending actions expire after 10 minutes.
"""
import hashlib
import json
from datetime import datetime, timedelta

from pydantic import BaseModel, Field, ValidationError

CONFIRM_TTL = timedelta(minutes=10)
DAYS_FR = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


class BookVisitArgs(BaseModel):
    """What `book_visit` needs, with rules pydantic enforces.

    - `listing_id`: "L" then 1-5 digits (`pattern` is a regex).
    - `when`: a real date-time; the string "2026-12-05T10:00" is converted.
    - `client_name`: 2 to 80 characters. `phone`: 8 to 12 digits, optional `+`.

    Example:
        >>> BookVisitArgs(listing_id="L12", when="2026-12-05T10:00", client_name="Amel", phone="22123456").when
        datetime.datetime(2026, 12, 5, 10, 0)
        >>> try:
        ...     BookVisitArgs(listing_id="12", when="2026-12-05T10:00", client_name="Amel", phone="call me")
        ... except ValidationError as e:
        ...     print([err["loc"][0] for err in e.errors()])
        ['listing_id', 'phone']
    """
    listing_id: str = Field(pattern=r"^L\d{1,5}$")
    when: datetime
    client_name: str = Field(min_length=2, max_length=80)
    phone: str = Field(pattern=r"^\+?\d{8,12}$")


TOOLS = {"book_visit": BookVisitArgs}     # the only actions the model may propose


def action_id(tool, args):
    """Same tool + same arguments -> same 16-hex id.

    `json.dumps(..., sort_keys=True)` gives the same text whatever the key
    order; `default=str` handles datetimes. Its SHA-256 is the id. So if
    the model proposes the same booking twice, it's one pending action, not two.

    Example:
        >>> action_id("t", {"a": 1, "b": 2}) == action_id("t", {"b": 2, "a": 1})
        True
        >>> action_id("t", {"a": 1}) == action_id("t", {"a": 2}), len(action_id("t", {"a": 1}))
        (False, 16)
    """
    return hashlib.sha256(json.dumps({"tool": tool, "args": args}, sort_keys=True, default=str).encode()).hexdigest()[:16]


def preview(tool, args):
    """The sentence the agent confirms, in plain French: no JSON, no ids
    they have to decode. `w.weekday()` is 0 for Monday, which indexes `DAYS_FR`.

    Example:
        >>> args = BookVisitArgs(listing_id="L12", when="2026-12-05T10:00", client_name="Amel", phone="22123456")
        >>> preview("book_visit", args)
        'Réserver une visite du bien L12 le samedi 05/12 à 10:00 pour Amel (22123456).'
    """
    if tool == "book_visit":
        w = args.when
        return f"Réserver une visite du bien {args.listing_id} le {DAYS_FR[w.weekday()]} {w:%d/%m} à {w:%H:%M} pour {args.client_name} ({args.phone})."
    return f"{tool}: {args.model_dump()}"


class ActionDesk:
    """Pending actions waiting for a human yes.

    `execute(tool, args_dict)` does the real work (an API call). `now` is a
    function returning the time, passed in so tests can move the clock.

    - `pending`: proposed, not yet confirmed.
    - `done`: confirmed and executed, with their result.
    - `audit`: one line per event, for "who booked what, when?".

    Example:
        >>> desk = ActionDesk(lambda tool, args: {"visit_id": 1})
        >>> desk.pending, desk.done, desk.audit
        ({}, {}, [])
    """

    def __init__(self, execute, now=datetime.now):
        self.execute, self.now = execute, now
        self.pending, self.done, self.audit = {}, {}, []

    def _log(self, aid, tool, status):
        self.audit.append({"at": self.now().isoformat(timespec="seconds"), "action_id": aid, "tool": tool, "status": status})

    def propose(self, tool, raw_args):
        """Validate a proposal and park it until someone confirms.

        - Unknown tool -> `invalid`, "unknown tool".
        - Bad arguments -> `invalid`, one message per pydantic error
          (`"phone: String should match pattern ..."`), which goes back to the
          model so it can fix its call.
        - Otherwise: stored as pending with its time, and the preview returned.

        Nothing is executed here.

        Example:
            >>> desk = ActionDesk(lambda tool, args: {"visit_id": 1})
            >>> r = desk.propose("book_visit", {"listing_id": "L12", "when": "2026-12-05T10:00", "client_name": "Amel", "phone": "22123456"})
            >>> r["status"], r["preview"]
            ('needs_confirmation', 'Réserver une visite du bien L12 le samedi 05/12 à 10:00 pour Amel (22123456).')
            >>> desk.propose("delete_all", {})
            {'status': 'invalid', 'errors': ['unknown tool']}
        """
        if tool not in TOOLS:
            self._log(None, tool, "invalid")
            return {"status": "invalid", "errors": ["unknown tool"]}
        try:
            args = TOOLS[tool](**raw_args)
        except ValidationError as e:
            self._log(None, tool, "invalid")
            return {"status": "invalid", "errors": [f"{'.'.join(map(str, err['loc']))}: {err['msg']}" for err in e.errors()]}
        aid = action_id(tool, args.model_dump())
        self.pending[aid] = {"tool": tool, "args": args, "at": self.now()}
        self._log(aid, tool, "proposed")
        return {"status": "needs_confirmation", "action_id": aid, "preview": preview(tool, args)}

    def confirm(self, aid):
        """Run a pending action, exactly once. The order of the checks matters:

        1. Already done -> `already_done` with the same result. A double click
           or a network retry never books twice (this is **idempotency**).
        2. Not pending -> `unknown`.
        3. Older than 10 minutes -> `expired` and dropped: a "yes" to an old
           preview may no longer be what the agent means.
        4. Execute. Success -> `done`. An exception -> `failed`, and the
           action **stays pending** so it can be retried.

        Example:
            >>> desk = ActionDesk(lambda tool, args: {"visit_id": 7})
            >>> aid = desk.propose("book_visit", {"listing_id": "L12", "when": "2026-12-05T10:00", "client_name": "Amel", "phone": "22123456"})["action_id"]
            >>> desk.confirm(aid)
            {'status': 'done', 'result': {'visit_id': 7}}
            >>> desk.confirm(aid)
            {'status': 'already_done', 'result': {'visit_id': 7}}
            >>> [e["status"] for e in desk.audit]
            ['proposed', 'done', 'already_done']
        """
        if aid in self.done:
            self._log(aid, self.done[aid]["tool"], "already_done")
            return {"status": "already_done", "result": self.done[aid]["result"]}
        p = self.pending.get(aid)
        if p is None:
            self._log(aid, None, "unknown")
            return {"status": "unknown"}
        if self.now() - p["at"] > CONFIRM_TTL:
            del self.pending[aid]
            self._log(aid, p["tool"], "expired")
            return {"status": "expired"}
        try:
            result = self.execute(p["tool"], p["args"].model_dump(mode="json"))
        except Exception as e:
            self._log(aid, p["tool"], "failed")
            return {"status": "failed", "error": str(e)}
        del self.pending[aid]
        self.done[aid] = {"tool": p["tool"], "result": result}
        self._log(aid, p["tool"], "done")
        return {"status": "done", "result": result}

    def cancel(self, aid):
        """The agent said no: remove the pending action. True if it was there.

        Example:
            >>> desk = ActionDesk(lambda tool, args: None)
            >>> aid = desk.propose("book_visit", {"listing_id": "L3", "when": "2026-12-05T10:00", "client_name": "Amel", "phone": "22123456"})["action_id"]
            >>> desk.cancel(aid), desk.cancel(aid), desk.confirm(aid)
            (True, False, {'status': 'unknown'})
        """
        p = self.pending.pop(aid, None)
        if p:
            self._log(aid, p["tool"], "cancelled")
        return p is not None


def run_with_my_api(url="http://127.0.0.1:8001"):
    """The real action: book through your day 31 visits API, asking you to confirm.

    Start the API first: `uvicorn visits_api:app --port 8001` in ../day31.

    Note: needs the day 31 API running and a terminal to type "o".
    """
    import httpx
    execute = lambda tool, args: httpx.post(f"{url}/visits", json={
        "name": args["client_name"], "phone": args["phone"], "listing_ids": [args["listing_id"]], "when": args["when"]}, timeout=10).raise_for_status().json()
    desk = ActionDesk(execute)
    p = desk.propose("book_visit", {"listing_id": "L12", "when": "2026-12-05T10:00", "client_name": "Amel", "phone": "22123456"})
    print(p)
    if p["status"] == "needs_confirmation" and input("Confirmer ? (o/n) ") == "o":
        print(desk.confirm(p["action_id"]))
        print(desk.confirm(p["action_id"]))         # second click: no double booking
    print(json.dumps(desk.audit, indent=1))


if __name__ == "__main__":
    import sys
    if "--real" in sys.argv:
        run_with_my_api()
    else:
        # Demo: a fake booking system and a clock we control.
        clock = {"t": datetime(2026, 12, 1, 9, 0)}
        bookings = []

        def execute(tool, args):
            if args["listing_id"] == "L99":
                raise RuntimeError("409 slot taken")
            bookings.append(args)
            return {"visit_id": len(bookings)}

        desk = ActionDesk(execute, now=lambda: clock["t"])
        amel = {"listing_id": "L12", "when": "2026-12-05T10:00", "client_name": "Amel", "phone": "22123456"}
        p = desk.propose("book_visit", amel)
        print("1. propose      ->", p["preview"])
        print("2. confirm      ->", desk.confirm(p["action_id"]))
        print("3. double click ->", desk.confirm(p["action_id"]))
        print("4. bad phone    ->", desk.propose("book_visit", dict(amel, phone="call me"))["errors"])
        p2 = desk.propose("book_visit", dict(amel, listing_id="L99"))
        print("5. slot taken   ->", desk.confirm(p2["action_id"]), "| still pending:", p2["action_id"] in desk.pending)
        p3 = desk.propose("book_visit", dict(amel, listing_id="L7"))
        clock["t"] += timedelta(minutes=11)
        print("6. 11 min later ->", desk.confirm(p3["action_id"]))
        print("bookings made:", len(bookings))
        print("audit:")
        for e in desk.audit:
            print("  ", e["at"], e["status"], e["action_id"])
