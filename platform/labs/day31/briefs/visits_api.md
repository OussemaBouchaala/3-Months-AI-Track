# An API the agent can act on
**Topic:** business rules belong in code behind the API, so no prompt (or prompt injection) can skip them.

## Real example
A clinic's booking endpoint. Whatever the chatbot says, the API refuses a Sunday or a booking in the past, and tells the caller exactly why:

```python
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

app = FastAPI()

class Appointment(BaseModel):
    patient: str
    when: datetime

@app.post("/appointments", status_code=201)
def book(a: Appointment):
    problems = []
    if a.when.weekday() == 6:
        problems.append("closed on Sunday")
    if a.when < datetime.now():
        problems.append("in the past")
    if problems:
        raise HTTPException(422, detail={"problems": problems})
    return {"patient": a.patient, "when": a.when.isoformat()}

client = TestClient(app)
next_monday = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
print(client.post("/appointments", json={"patient": "Amel", "when": next_monday.replace(hour=10).isoformat()}).status_code)
print(client.post("/appointments", json={"patient": "Amel", "when": "2020-01-05T10:00"}).json())
```

## Your mission
Build `POST /visits` and `GET /visits` with the handbook's rules enforced in code.

## Steps
1. `check_rules`: four rules, one message each (exact text from the docstring).
2. `book_visit`: rules → 422 with the problems; same listing and time → 409; else store with an id.
3. `list_visits`: filter by phone when given.
4. In a terminal: `uvicorn visits_api:app --port 8003 --reload`, then open http://127.0.0.1:8003/docs and try it.

## Done when
**Check** passes: valid bookings get 201, each broken rule gets 422 with its reason, double booking gets 409.
