import numpy as np
from sklearn.model_selection import TimeSeriesSplit

X = np.arange(12).reshape(-1, 1)
for train, test in TimeSeriesSplit(n_splits=3).split(X):
    print("train", train, "test", test)
