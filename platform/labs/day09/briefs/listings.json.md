# Your test set
**Topic:** 10 real listings with hand-written labels, reused all week.

## Real example
Two labelled items, the format your test set uses. Note `null` when the listing doesn't say, and prices as plain numbers:

```json
[
  {"text": "S+2 à Sahloul, 120 m², 250 000 DT, proche de toutes commodités",
   "label": {"price_tnd": 250000, "surface_m2": 120, "rooms": 3, "city": "Sousse"}},
  {"text": "للبيع شقة في المنار، 3 غرف، السعر عند الاتصال",
   "label": {"price_tnd": null, "surface_m2": null, "rooms": 3, "city": "Tunis"}}
]
```

"S+2" in Tunisia means a living room + 2 bedrooms: decide once how you count `rooms` and stick to it.

## Your mission
Collect listings in Arabic, French and English and label the four fields yourself.

## Steps
1. Copy listings from [Tayara](https://www.tayara.tn) or [Mubawab](https://www.mubawab.tn).
2. One object per listing: `text` and `label` with `price_tnd`, `surface_m2`, `rooms`, `city`.
3. Use `null` when the listing doesn't say.
