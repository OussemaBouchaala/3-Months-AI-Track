fit = fn("fit_degree")
r1, r4, r15 = fit(1), fit(4), fit(15)
check("fit_degree returns (train_mse, val_mse)", isinstance(r1, tuple) and len(r1) == 2,
      "return train_mse, val_mse")
check("degree 1 underfits: both errors are high", lambda: r1[0] > 0.15 and r1[1] > 0.15)
check("degree 4 beats degree 1 on validation", lambda: r4[1] < r1[1])
check("degree 15 fits the train set better than degree 4", lambda: r15[0] < r4[0])
check("degree 15 has a bigger train/validation gap than degree 4", lambda: (r15[1] - r15[0]) > (r4[1] - r4[0]))
import re
code = re.sub(r"#.*", "", src)
check("You plotted train and validation MSE", code.count(".plot(") >= 2,
      "Use plt.plot(degrees, train_mse, label='train') and the same for validation.")
check("BEST_DEGREE is the degree with the lowest validation MSE",
      lambda: var("BEST_DEGREE") == min(range(1, 16), key=lambda d: fit(d)[1]),
      "Run the file and read the degree with the lowest val MSE.")
check("You explained why high degrees fail", lambda: filled(var("WHY_HIGH_DEGREES_FAIL"), 15))
