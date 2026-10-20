import numpy as np
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y, Xn, yn = var("X"), var("y"), var("X_noise"), var("y_noise")
ref_leaky = cross_val_score(KNeighborsClassifier(), StandardScaler().fit_transform(X), y, cv=5).mean()
ref_pipe = cross_val_score(make_pipeline(StandardScaler(), KNeighborsClassifier()), X, y, cv=5).mean()
check("leaky_scaler_score scales ALL rows first", lambda: approx(fn("leaky_scaler_score")(X, y), ref_leaky),
      f"Expected {ref_leaky:.4f}.")
check("pipeline_scaler_score uses a Pipeline", lambda: approx(fn("pipeline_scaler_score")(X, y), ref_pipe),
      f"Expected {ref_pipe:.4f}.")
check("leaky selection 'learns' pure noise (> 0.70)", lambda: fn("leaky_select_score")(Xn, yn) > 0.70,
      "Select the 20 columns on all of X_noise, then cross-validate.")
check("the pipeline shows the truth on noise (about 0.5)", lambda: abs(fn("pipeline_select_score")(Xn, yn) - 0.5) < 0.15,
      "make_pipeline(SelectKBest(f_classif, k=k), LogisticRegression(max_iter=1000)).")
check("You explained why the gaps differ", lambda: filled(var("WHY_THE_GAPS_DIFFER"), 20))
