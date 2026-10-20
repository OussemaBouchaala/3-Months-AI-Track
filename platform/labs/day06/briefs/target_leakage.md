# Target leakage
**Topic:** a feature only known because of the label makes any model look perfect.

## Your mission
Build a leaky feature on purpose and watch the score jump.

## Steps
1. `leak = y + rng.normal(0, 0.1, n)`.
2. `cv_score`: mean 5-fold accuracy of `LogisticRegression(max_iter=1000)`.
3. **Run**: honest vs leaky.
4. Write one real example from your own work in `MY_EXAMPLE`.

## Done when
**Check** sees a modest honest score and a near-perfect leaky one.
