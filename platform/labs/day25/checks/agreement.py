ag, ck = fn("agreement"), fn("cohen_kappa")
check("agreement([1,0,1,1], [1,1,1,0]) = 0.5", lambda: ag([1, 0, 1, 1], [1, 1, 1, 0]) == 0.5)
check("confusion counts the 4 cases", lambda: fn("confusion")([1, 1, 0, 0, 1], [1, 0, 1, 0, 1]) == {"both_1": 2, "both_0": 1, "judge_too_kind": 1, "judge_too_harsh": 1})
a = [0, 0, 0, 0, 0, 0, 0, 0, 1, 0]
b = [0, 0, 0, 0, 0, 0, 0, 1, 0, 0]
check("kappa removes chance agreement (80% agreement, kappa < 0)", lambda: ck(a, b) < 0)
check("kappa of identical labels is 1", lambda: ck([1, 0, 1, 0], [1, 0, 1, 0]) == 1.0)
check("kappa value", lambda: abs(ck([1, 1, 0, 0, 1, 0], [1, 0, 0, 0, 1, 1]) - 1 / 3) < 1e-9,
      "p_o = 4/6, p_e = 0.5*0.5 + 0.5*0.5 = 0.5, kappa = (0.667 - 0.5) / 0.5")
check("kappa when everyone always says 1 -> 1.0 (no division by zero)", lambda: ck([1, 1], [1, 1]) == 1.0)
v = fn("verdict")
check("verdict thresholds", lambda: (v(0.85), v(0.7), v(0.3)) == ("trust", "spot-check", "fix the judge prompt"))
mine, judge = var("MY_LABELS"), var("JUDGE_LABELS")
check("you graded 20 answers and the judge graded the same 20", lambda: len(mine) == len(judge) == 20 and set(mine) | set(judge) <= {0, 1},
      "Grade your own first, then run the judge on the same answers.")
