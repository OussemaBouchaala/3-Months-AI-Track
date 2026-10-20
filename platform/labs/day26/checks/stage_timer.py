import statistics
import time

ST = var("StageTimer")


def timed():
    t = ST()
    with t.stage("a"):
        time.sleep(0.02)
    with t.stage("b"):
        time.sleep(0.01)
    with t.stage("a"):
        time.sleep(0.02)
    return t


check("stage() records seconds per stage", lambda: set(timed().times) == {"a", "b"} and 0.009 < timed().times["b"] < 0.2)
check("the same stage twice is added up", lambda: timed().times["a"] >= 0.04)
check("total() is the sum of stages", lambda: (lambda t: abs(t.total() - sum(t.times.values())) < 1e-9)(timed()))


def raising():
    t = ST()
    try:
        with t.stage("boom"):
            time.sleep(0.01)
            raise ValueError
    except ValueError:
        pass
    return t


check("a stage that raises is still timed (try/finally)", lambda: raising().times.get("boom", 0) > 0.005)
qc = fn("query_cost")
check("query_cost: generation tokens", lambda: abs(qc(1000, 100, 3, 15) - 0.0045) < 1e-12)
check("query_cost adds judge calls", lambda: abs(qc(1000, 100, 3, 15, judge_calls=2, judge_cost=0.001) - 0.0065) < 1e-12)


class Fake:
    def __init__(self, a, b):
        self.times = {"embed": a, "generate": b}

    def total(self):
        return sum(self.times.values())


fakes = [Fake(0.1 * i, 1.0 + i) for i in range(1, 21)]
rep = lambda: fn("stage_report")(fakes)
q = lambda xs: (statistics.quantiles(xs, n=100, method="inclusive")[49], statistics.quantiles(xs, n=100, method="inclusive")[94])
check("stage_report has every stage plus total", lambda: set(rep()) == {"embed", "generate", "total"})
check("stage_report gives (p50, p95) per stage", lambda: all(abs(x - y) < 1e-9 for x, y in zip(rep()["generate"], q([f.times["generate"] for f in fakes]))))
check("total uses each query's total()", lambda: all(abs(x - y) < 1e-9 for x, y in zip(rep()["total"], q([f.total() for f in fakes]))))
