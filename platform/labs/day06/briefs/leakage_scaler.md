# Leaky vs honest preprocessing
**Topic:** anything fitted on all the data before cross-validation leaks the test folds.

## Your mission
Score the same models leaky and inside a Pipeline, for a scaler and for feature selection.

## Steps
1. `leaky_scaler_score`: scale all of X, then `cross_val_score`.
2. `pipeline_scaler_score`: `make_pipeline(StandardScaler(), KNeighborsClassifier())`.
3. `leaky_select_score` / `pipeline_select_score`: the same with `SelectKBest(f_classif, k=k)` on pure noise.
4. **Run** and explain why the gaps differ.

## Done when
**Check** sees the leaky selection "learn" noise and the pipeline stay near 0.5.
