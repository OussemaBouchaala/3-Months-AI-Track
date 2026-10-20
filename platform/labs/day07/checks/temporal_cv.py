import functools

import numpy as np
from sklearn.model_selection import KFold, TimeSeriesSplit


@functools.lru_cache(None)
def series(n):
    return np.asarray(fn("make_series")(n))


def lags():
    return fn("lag_features")(np.arange(10.0), lags=3)


@functools.lru_cache(None)
def scores():
    X, t = fn("lag_features")(series(600))
    s = fn("score")
    return float(s(KFold(5, shuffle=True, random_state=0), X, t)), float(s(TimeSeriesSplit(5), X, t))


check("make_series returns n values", lambda: len(series(300)) == 300)
check("make_series is autocorrelated (a random walk)",
      lambda: np.corrcoef(series(300)[:-1], series(300)[1:])[0, 1] > 0.9, "Use np.cumsum on the noise.")
check("lag_features returns len(y) - lags rows", lambda: lags()[0].shape == (7, 3) and len(lags()[1]) == 7)
check("first row is [y[2], y[1], y[0]] with target y[3]", lambda: list(lags()[0][0]) == [2, 1, 0] and lags()[1][0] == 3)
check("score returns a mean R^2 for each splitter", lambda: len(scores()) == 2)
check("shuffled KFold looks much better than TimeSeriesSplit", lambda: scores()[0] - scores()[1] > 0.2,
      "Shuffling lets the forest see neighbours of every test point; forward splits must extrapolate.")
check("You explained the gap", lambda: filled(var("GAP_EXPLANATION"), 30))
check("Bonus: groups_stay_apart works with GroupKFold",
      lambda: fn("groups_stay_apart")(np.zeros((80, 1)), np.repeat(np.arange(8), 10)) is True)
