# Choose a threshold
**Topic:** 0.5 is only a default; pick the threshold from the cost of each error.

## Your mission
Find the threshold with the best precision while still catching 80% of positives.

## Steps
1. In `best_threshold`, keep indexes where `recall >= min_recall`.
2. Among them, take the one with the highest precision; return threshold, precision, recall.
3. **Run**, then mark your point on the curve with `plt.scatter`.

## Done when
**Check** matches the reference choice for recall 0.8 and 0.95.
