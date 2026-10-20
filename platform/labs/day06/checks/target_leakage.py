import numpy as np

y, X_honest = var("y"), var("X_honest")
leak = np.asarray(var("leak"), dtype=float)
check("leak has one value per row", lambda: leak.shape == y.shape, "leak = y + rng.normal(0, 0.1, n)")
check("leak is computed from the label", lambda: np.corrcoef(leak, y)[0, 1] > 0.9)
cv = fn("cv_score")
check("honest score is modest (0.55-0.80)", lambda: 0.55 < cv(X_honest, y) < 0.80)
check("leaky score is near perfect (> 0.95)", lambda: cv(var("X_leaky"), y) > 0.95)
check("You gave a real example from your work", lambda: filled(var("MY_EXAMPLE"), 20))
