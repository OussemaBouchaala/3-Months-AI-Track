human = [1] * 18 + [0, 0]
judge = [1] * 20
p_o = sum(h == j for h, j in zip(human, judge)) / 20
ph, pj = sum(human) / 20, sum(judge) / 20
p_e = ph * pj + (1 - ph) * (1 - pj)
kappa = 0.0 if p_e == 1 else (p_o - p_e) / (1 - p_e)
print(f"agreement {p_o:.2f}  chance {p_e:.2f}  kappa {kappa:.2f}")
