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
    model = make_pipeline(PolynomialFeatures(degree), LinearRegression())
    model.fit(X_train, y_train)
    return mean_squared_error(y_train, model.predict(X_train)), mean_squared_error(y_val, model.predict(X_val))


if __name__ == "__main__":
    degrees = list(range(1, 16))
    train_mse, val_mse = zip(*[fit_degree(d) for d in degrees])
    for d, tr, va in zip(degrees, train_mse, val_mse):
        print(f"degree {d:>2}: train {tr:.3f}   val {va:.3f}")

    # TODO: plot train_mse and val_mse against degrees on one chart
    #       (plt.plot twice with labels, plt.yscale("log"), axis labels, plt.legend())
    # Plot train_mse and val_mse against degrees on one chart
    plt.figure(figsize=(8, 5))
    plt.plot(degrees, train_mse, marker='o', label="Train MSE")
    plt.plot(degrees, val_mse, marker='s', label="Validation MSE")
    plt.yscale("log")
    plt.xlabel("Polynomial Degree")
    plt.ylabel("Mean Squared Error (Log Scale)")
    plt.title("Train vs Validation MSE by Polynomial Degree")
    plt.legend()
    plt.grid(True, which="both", ls="--")
    plt.show()

# After running: which degree has the lowest validation error, and why do high degrees fail?
BEST_DEGREE = 3
WHY_HIGH_DEGREES_FAIL = "high degrees fail because they chase noise and the variance vary high so the validation error increase significantly"
