# The cost model
**Topic:** per-query API cost with caching, local hardware cost per month, capacity at peak, and the break-even volume.

## Real example
Renting vs buying a delivery van (a different cost decision, the same break-even logic):

```python
import math
rent_per_day = 120          # TND
buy_monthly = 1500 + 400    # loan + insurance and maintenance, TND
print("buying wins above", math.ceil(buy_monthly / rent_per_day), "days of use per month")
```

Below 16 days a month, renting is cheaper. The same shape decides API vs local GPU: a fixed monthly cost against a price per use.

## Your mission
Turn your token counts and the agency's volume into a monthly bill for each option.

## Steps
1. Update `PRICES` from the providers' pricing pages (date them in a comment).
2. `query_cost` with cached input, `local_monthly`, `gpus_needed`.
3. `break_even` and `cost_table`.
4. **Run** with your real average tokens per query (from your logs) and the volume from the interview.

## Done when
**Check** passes and you can say which option is cheaper at the agency's volume, and from which volume that flips.
