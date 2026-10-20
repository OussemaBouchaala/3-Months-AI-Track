# Read a learning curve
**Topic:** curves that stay apart mean variance; curves that meet low mean bias.

## Your mission
Compare an unlimited decision tree with `max_depth=3` as the training set grows.

## Steps
1. `curve`: call `learning_curve(model, X, y, cv=5, train_sizes=np.linspace(0.1, 1.0, 8))` and average the scores with `.mean(axis=1)`.
2. **Run**: two charts appear side by side.
3. Describe how the gap changes in `GAP_EXPLANATION`.

## Done when
**Check** sees a ~100% train score for the deep tree and a smaller gap at depth 3.
