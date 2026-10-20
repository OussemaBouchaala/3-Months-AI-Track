# Underfit vs overfit: train and validation error as polynomial degree grows.
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures

rng = np.random.default_rng(0)
X = rng.uniform(0, 1, size=(40, 1))
y = np.sin(2 * np.pi * X[:, 0]) + rng.normal(0, 0.2, size=40)
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.3, random_state=0)


def fit_degree(degree):
    """Fit make_pipeline(PolynomialFeatures(degree), LinearRegression()) on the TRAIN split.
    Return (train_mse, val_mse) using mean_squared_error."""
    # TODO
    ...


if __name__ == "__main__":
    degrees = list(range(1, 16))
    train_mse, val_mse = zip(*[fit_degree(d) for d in degrees])
    for d, tr, va in zip(degrees, train_mse, val_mse):
        print(f"degree {d:>2}: train {tr:.3f}   val {va:.3f}")

    # TODO: plot train_mse and val_mse against degrees on one chart
    #       (plt.plot twice with labels, plt.yscale("log"), axis labels, plt.legend())
    plt.show()

# After running: which degree has the lowest validation error, and why do high degrees fail?
BEST_DEGREE = None
WHY_HIGH_DEGREES_FAIL = ""
