# Why random splits lie on time series
**Topic:** neighbouring time steps are near-duplicates; forward splits are the honest test.

## Your mission
Score the same forest with shuffled K-fold and with `TimeSeriesSplit`, and explain the gap.

## Steps
1. `make_series`: `np.cumsum(noise) + 2 * np.sin(2 * np.pi * t / 24)`.
2. `lag_features`: rows `[y[t-1], ..., y[t-lags]]`, target `y[t]`.
3. `score`: mean R² of the forest under a given splitter.
4. **Run**, then link the gap to your MmCows result in `GAP_EXPLANATION`.
5. Bonus: `groups_stay_apart` with `GroupKFold`.

## Done when
**Check** sees shuffled K-fold score far above `TimeSeriesSplit`.
