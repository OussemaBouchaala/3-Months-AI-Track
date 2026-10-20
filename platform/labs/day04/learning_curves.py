# Learning curves: an unlimited tree (high variance) vs max_depth=3.
import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import learning_curve
from sklearn.tree import DecisionTreeClassifier

X, y = load_breast_cancer(return_X_y=True)


def curve(model):
    """Call learning_curve(model, X, y, cv=5, train_sizes=np.linspace(0.1, 1.0, 8)).
    Return (train_sizes, train_mean, val_mean): the scores averaged over folds (axis=1)."""
    # TODO
    ...


def plot_curve(ax, model, title):
    sizes, train, val = curve(model)
    ax.plot(sizes, train, "o-", label="train")
    ax.plot(sizes, val, "o-", label="validation")
    ax.set(title=title, xlabel="training examples", ylabel="accuracy")
    ax.legend()


if __name__ == "__main__":
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    plot_curve(axes[0], DecisionTreeClassifier(random_state=0), "no depth limit")
    plot_curve(axes[1], DecisionTreeClassifier(max_depth=3, random_state=0), "max_depth=3")
    plt.show()

# After running: how does the train/validation gap change with max_depth=3, and what does it tell you?
GAP_EXPLANATION = ""
