# Underfit to overfit
**Topic:** the gap between train and validation error tells bias from variance.

## Your mission
Fit polynomials of degree 1 to 15 and watch both errors.

## Steps
1. `fit_degree`: `make_pipeline(PolynomialFeatures(degree), LinearRegression())`, fit on train, return both MSEs.
2. **Run** and read the table.
3. Plot train and validation MSE against degree (two `plt.plot` calls, log scale).
4. Set `BEST_DEGREE` and explain why high degrees fail.

## Done when
**Check** sees underfitting at 1, overfitting at 15, and your best degree.
