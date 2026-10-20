# The accuracy trap
**Topic:** with 0.5% positives, "always negative" scores 99.5% accuracy and catches nothing.

## Your mission
Score a do-nothing model and a real one with six metrics, and find the ones that expose the fake.

## Steps
1. In `evaluate`, return a dict with `accuracy`, `precision`, `recall`, `f1` (from `y_pred`) and `roc_auc`, `pr_auc` (from `scores`).
2. **Run** and compare the dummy with logistic regression.
3. List the revealing metric names in `EXPOSES_DUMMY`.

## Done when
**Check** confirms all six metrics and the ones you picked.
