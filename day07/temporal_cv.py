# Why shuffled K-fold lies on time series: compare it with forward-chaining splits.
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupKFold, KFold, TimeSeriesSplit, cross_val_score

N = 1500


def make_series(n=N, seed=0):
    """Autocorrelated series: a random walk plus daily seasonality.
    y[t] = cumsum(noise)[t] + 2 * sin(2 * pi * t / 24), with noise ~ Normal(0, 1)."""
    rng = np.random.default_rng(seed)
    t = np.arange(n)
    # TODO
    noise = rng.normal(loc=0.0, scale=1.0, size=n)
    trend = np.cumsum(noise)
    seasonality = 2.0 * np.sin(2.0 * np.pi * t / 24.0)
    return trend + seasonality


def lag_features(y, lags=3):
    """Supervised table from a series. For every t >= lags:
    X row = [y[t-1], y[t-2], ..., y[t-lags]], target = y[t].
    Return (X, target) as numpy arrays with len(y) - lags rows."""
    # TODO
    n_samples = len(y) - lags
    X = np.zeros((n_samples, lags))
    for i in range(1, lags + 1):
        X[:, i - 1] = y[lags - i : -i]
    target = y[lags:]
    return X, target


def score(cv, X, target):
    """Mean R^2 of RandomForestRegressor(n_estimators=100, random_state=0) under cross-validator cv."""
    # TODO
    rf = RandomForestRegressor(n_estimators=100, random_state=0)
    scores = cross_val_score(rf, X, target, cv=cv, scoring="r2")
    return np.mean(scores)


def groups_stay_apart(X, groups, n_splits=4):
    """Bonus: return True if, for every GroupKFold(n_splits) split of X,
    no group id appears in both the train and the test indexes."""
    # TODO (bonus)
    gkf = GroupKFold(n_splits=n_splits)
    for train_idx, test_idx in gkf.split(X, groups=groups):
        train_groups = set(groups[train_idx])
        test_groups = set(groups[test_idx])
        if not train_groups.isdisjoint(test_groups):
            return False
    return True


if __name__ == "__main__":
    y = make_series()
    X, target = lag_features(y)
    print("shuffled KFold  R2:", round(score(KFold(5, shuffle=True, random_state=0), X, target), 3))
    print("TimeSeriesSplit R2:", round(score(TimeSeriesSplit(5), X, target), 3))

# After running: explain the gap between the two scores, and link it to your MmCows result.
GAP_EXPLANATION = """
Shuffled K-Fold creates severe data leakage in time-series models due to auto-correlation and overlapping lag features. When data is randomly shuffled:
1. Interpolation Leakage: The model predicts y[t] using y[t-1], y[t-2], etc., where y[t-1] and y[t+1] are present in the training set. It reduces forecasting to simple local interpolation, giving wildly optimistic R^2 scores (~0.95+).
2. Lookahead Bias: The model trains on future data to predict past data, violating the fundamental causal direction of time.

In contrast, TimeSeriesSplit (forward-chaining) respects the temporal order by evaluating the model purely on unseen future steps, reflecting true out-of-sample generalization (~0.0 or negative R^2).

Connection to MmCows:
In the MmCows setup, multiple consecutive measurements belong to the same entity (cow/group). Standard K-Fold splits samples randomly, putting observations of the same cow into both train and test sets. The model simply memorizes individual cows rather than learning general patterns. GroupKFold solves this by ensuring all observations of a given group (or cow) stay strictly isolated within either train or test, preventing identity leakage just as TimeSeriesSplit prevents temporal leakage.
"""
