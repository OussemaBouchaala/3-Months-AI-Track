# Shallow vs deep copy
**Topic:** `.copy()` copies the outer container only; `copy.deepcopy()` copies everything inside.

## Your mission
Copy a model config two ways, change the original, and see which copy follows.

## Steps
1. `shallow = config.copy()` and `deep = copy.deepcopy(config)`.
2. Predict the three prints, then **Run**.
3. Explain why `shallow["layers"]` changed but `shallow["lr"]` did not.

## Done when
**Check** confirms the shallow copy shares `layers` and the deep copy doesn't.
