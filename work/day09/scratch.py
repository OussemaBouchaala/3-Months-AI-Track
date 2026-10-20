import json
from pydantic import BaseModel

class Listing(BaseModel):
    price_tnd: float | None
    rooms: int | None

prompt = (
    "Extract the fields from this listing. Reply with JSON ONLY matching this schema:\n"
    + json.dumps(Listing.model_json_schema())
    + "\n\nListing: S+2 à Sahloul, 250 000 DT"
)
print(prompt)
