import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(0)
x = np.sort(rng.uniform(0, 1, 20))
y = np.sin(2 * np.pi * x) + rng.normal(0, 0.2, 20)

xs = np.linspace(0, 1, 200)
for deg in (1, 4, 15):
    coefs = np.polyfit(x, y, deg)
    plt.plot(xs, np.polyval(coefs, xs), label=f"degree {deg}")
plt.scatter(x, y, c="k", s=15)
plt.ylim(-2, 2); plt.legend(); plt.show()
