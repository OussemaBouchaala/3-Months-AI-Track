# Choose the project
**Topic:** a weighted decision matrix, plus a sensitivity check so you know if the choice is solid or a coin flip.

## Real example
Choosing between three used cars (a different decision, same method):

```python
weights = {"price": 3, "reliability": 2, "comfort": 1}
cars = {"Polo": {"price": 4, "reliability": 4, "comfort": 3},
        "Clio": {"price": 5, "reliability": 3, "comfort": 3},
        "Golf": {"price": 2, "reliability": 5, "comfort": 5}}
total = sum(weights.values())
for name, s in cars.items():
    print(name, round(sum(w / total * s[k] for k, w in weights.items()), 2))
```

Polo and Clio are within 0.17 of each other: change the "price" weight by one and the winner may flip. That's what `sensitivity` tells you.

## Your mission
Score your real Phase 2 options and pick one you can defend.

## Steps
1. Edit `CRITERIA` and `OPTIONS` with your real candidates (keep scores 1-5).
2. `normalize_weights`, `weighted_score`, `rank`.
3. `sensitivity`: nudge each weight up and down by 1 and see whether the winner changes.
4. **Run**. If the winner is fragile, talk to one real user before deciding.

## Done when
**Check** passes and you can name your project in one sentence.
