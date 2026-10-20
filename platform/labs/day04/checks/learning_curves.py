from sklearn.tree import DecisionTreeClassifier

curve = fn("curve")
deep = curve(DecisionTreeClassifier(random_state=0))
shallow = curve(DecisionTreeClassifier(max_depth=3, random_state=0))
check("curve returns (sizes, train_mean, val_mean) with 8 points each",
      lambda: len(deep) == 3 and all(len(a) == 8 for a in deep),
      "Average the score arrays with .mean(axis=1).")
check("the unlimited tree scores ~100% on its own training data", lambda: deep[1][-1] > 0.99)
check("max_depth=3 has a smaller train/validation gap",
      lambda: (deep[1][-1] - deep[2][-1]) > (shallow[1][-1] - shallow[2][-1]))
check("You described the gap", lambda: filled(var("GAP_EXPLANATION"), 20))
