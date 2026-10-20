"""Week 1: Fundamentals + GitHub (Oct 5-11, 2026).

Exercise starters and checks live in labs/dayNN/ (see lab_files.py)."""
from lab_files import lab

DAY1 = {
    "id": "w1d1", "folder": "day01", "notes_task": 5, "date": "2026-10-05", "weekday": "Mon",
    "title": "Mutable defaults and references", "minutes": 75,
    "why": "You missed Q1. Python passes references to objects, and default arguments are created once.",
    "lesson": """
## Names point to objects

A variable doesn't contain a value. It's a name pointing to an object. Assignment never copies; it points another name at the same object.

```python
a = [1, 2, 3]
b = a          # same list, no copy
b.append(4)
print(a)       # [1, 2, 3, 4]
print(a is b, id(a) == id(b))
```

`==` asks "same value?", `is` asks "same object?", and `id()` shows identity.

## Mutable vs immutable

Immutable objects (int, str, tuple) can't change, so any "change" makes a new object and moves the name. Mutable objects (list, dict, set) change in place, and every name pointing at them sees it.

```python
x = 10; y = x; y += 1
print(x)       # 10: int is immutable, y was rebound

a = [1]; b = a; b += [2]
print(a)       # [1, 2]: list += mutates in place
```

## Functions get references too

A parameter is a new name for the caller's object. Mutating it changes the caller's object; reassigning it doesn't.

```python
def mutate(lst): lst.append(99)
def rebind(lst): lst = [99]

data = [1]
mutate(data); print(data)
rebind(data); print(data)
```

## The mutable default trap

Default values are created once, when the `def` line runs, and reused on every call.

```python
def add(x, items=[]):
    items.append(x)
    return items

print(add(1), add(2))
print(add.__defaults__)
```

Fix: use `None` as a sentinel and build a fresh object inside. In a long-running FastAPI server, a mutable default leaks data between requests.

## Shallow vs deep copy

`.copy()`, `list(a)`, `a[:]` copy only the outer container. `copy.deepcopy()` copies everything inside.

```python
import copy
a = [[1, 2], [3, 4]]
s, d = a.copy(), copy.deepcopy(a)
a[0].append(99)
print(s)
print(d)
```
""",
    "files": [
        lab("day01", "defaults.py", task=1),
        lab("day01", "aliasing.py", task=2),
        lab("day01", "copies.py", task=3),
        lab("day01", "puzzles.py", task=4),
    ],
    "tasks": [
        "Read the [Python FAQ entry on shared default values](https://docs.python.org/3/faq/programming.html#why-are-default-values-shared-between-objects)",
        "Part A: reproduce the items=[] bug, fix it, and show the log_request leak",
        "Part B: aliasing and id(), including b += [5] vs b = b + [5]",
        "Part C: shallow vs deep copy on the config dict",
        "Part D: predict all 4 puzzles before running; check misses in [Python Tutor](https://pythontutor.com/visualize.html#mode=edit)",
        "Notes: explain the mutable default bug in 3-5 lines",
        "GitHub: commit the new [profile README](https://github.com/OussemaBouchaala/OussemaBouchaala) ([how profile READMEs work](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-github-profile/customizing-your-profile/managing-your-profile-readme))",
    ],
    "done_when": "You can predict the output of any default-argument puzzle before running it.",
    "resources": [
        {"label": "Python FAQ: default values shared", "url": "https://docs.python.org/3/faq/programming.html#why-are-default-values-shared-between-objects"},
        {"label": "Python Tutor (visualize references)", "url": "https://pythontutor.com"},
    ],
    "quiz": [
        {"q": "What does this print?\na = [1, 2]; b = a; b = b + [3]; print(a)", "options": ["[1, 2]", "[1, 2, 3]", "TypeError", "[3]"], "answer": 0,
         "explain": "b + [3] builds a new list and rebinds b. a still points to the original."},
        {"q": "Which gives a fully independent copy of [[1], [2]]?", "options": ["x.copy()", "list(x)", "x[:]", "copy.deepcopy(x)"], "answer": 3,
         "explain": "The first three are shallow: the inner lists are shared. Only deepcopy copies them too."},
        {"q": "What does this print?\ndef f(d={}): d['n'] = d.get('n', 0) + 1; return d['n']\nf(); f(); print(f())", "options": ["1", "3", "0", "KeyError"], "answer": 1,
         "explain": "The dict default is created once, so the counter persists across calls: 1, 2, 3."},
    ],
}

DAY2 = {
    "id": "w1d2", "folder": "day02", "notes_task": 3, "date": "2026-10-06", "weekday": "Tue",
    "title": "Async and the event loop in FastAPI", "minutes": 75,
    "why": "You missed Q2, and your services run on FastAPI. Blocking the loop is a real production bug.",
    "lesson": """
## One thread, many tasks

asyncio runs an event loop on a single thread. A coroutine runs until it hits `await`, then hands control back so other tasks can run. Concurrency comes from waiting cooperatively, not from parallel threads.

```python
import asyncio, time

async def job(n):
    await asyncio.sleep(1)   # yields to the loop while waiting
    return n

async def main():
    t = time.perf_counter()
    print(await asyncio.gather(job(1), job(2), job(3)))
    print(f"{time.perf_counter() - t:.2f}s")

asyncio.run(main())
```

Three 1-second waits finish in about 1 second total.

## Blocking calls freeze everything

`time.sleep`, `requests.get`, a synchronous database driver, or heavy CPU work inside a coroutine never yields. The whole loop stops, so every other request waits.

```python
import asyncio, time

async def bad(n):
    time.sleep(1)            # blocks the loop
    return n

async def main():
    t = time.perf_counter()
    await asyncio.gather(bad(1), bad(2), bad(3))
    print(f"{time.perf_counter() - t:.2f}s")

asyncio.run(main())
```

## How FastAPI treats your endpoints

- `async def` endpoints run directly on the event loop. Only use non-blocking (awaitable) I/O inside them.
- Plain `def` endpoints run in a thread pool, so blocking code there doesn't freeze the loop.
- If you must call blocking code from `async def`, use `await run_in_threadpool(fn, *args)`.

## Today's experiment

You'll run a small FastAPI app **in your terminal** (servers can't run inside Bench, since they never finish), then fire concurrent requests at it from `load_test.py` here.

```bash
cd ml-fundamentals-lab/day02
uvicorn app_async:app --port 8001
```
""",
    "files": [
        lab("day02", "app_async.py", task=1),
        lab("day02", "load_test.py", task=2),
    ],
    "tasks": [
        "Read the [FastAPI page on concurrency and async/await](https://fastapi.tiangolo.com/async/)",
        "Build the 4 endpoints in app_async.py and start it with uvicorn",
        "Complete load_test.py; predict the 4 timings, then run",
        "Notes: a table of your measured timings and why each behaves that way",
    ],
    "done_when": "You can predict the timings before running them.",
    "resources": [
        {"label": "FastAPI: Concurrency and async/await", "url": "https://fastapi.tiangolo.com/async/"},
        {"label": "Real Python: Async IO", "url": "https://realpython.com/async-io-python/"},
    ],
    "quiz": [
        {"q": "Where does FastAPI run a plain `def` endpoint?", "options": ["On the event loop", "In a thread pool", "In a separate process", "It refuses to run it"], "answer": 1,
         "explain": "Sync endpoints go to a thread pool so blocking code doesn't freeze the loop."},
        {"q": "Inside `async def`, how do you wait 2 seconds without blocking?", "options": ["time.sleep(2)", "await time.sleep(2)", "await asyncio.sleep(2)", "asyncio.sleep(2)"], "answer": 2,
         "explain": "asyncio.sleep is awaitable and yields to the loop. Without await it does nothing; time.sleep blocks."},
        {"q": "5 concurrent requests hit `async def` with `time.sleep(2)`, one worker. Total time?", "options": ["About 2s", "About 10s", "About 0s", "About 5s"], "answer": 1,
         "explain": "Each request blocks the single loop for 2s, so they run one after another."},
    ],
}

DAY3 = {
    "id": "w1d3", "folder": "day03", "notes_task": 4, "date": "2026-10-07", "weekday": "Wed",
    "title": "Generators, decorators, context managers", "minutes": 75,
    "why": "Standard interview territory, and all three show up in ML and API code.",
    "lesson": """
## Generators: values on demand

A function with `yield` returns a generator. It produces one value at a time and keeps its state between them, so it never builds the whole sequence in memory.

```python
def count_up(n):
    for i in range(n):
        yield i

g = count_up(3)
print(next(g), next(g), list(g))
print(list(g))   # exhausted: a generator runs once
```

Use them to stream large files, batches, or API pages.

## Decorators: functions that wrap functions

A decorator takes a function and returns a new one. It works because inner functions remember variables from the enclosing scope (closures). `functools.wraps` keeps the original name and docstring.

```python
import functools, time

def timed(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        print(f"{fn.__name__} took {time.perf_counter() - start:.4f}s")
        return result
    return wrapper

@timed
def work():
    return sum(range(1_000_000))

work()
print(work.__name__)
```

## Context managers: guaranteed cleanup

`with` runs setup, your block, then cleanup, even if the block raises. You can write one as a class (`__enter__` / `__exit__`) or with `@contextmanager` and `try/finally`.

```python
from contextlib import contextmanager
import time

@contextmanager
def timer(label):
    start = time.perf_counter()
    try:
        yield
    finally:
        print(f"{label}: {time.perf_counter() - start:.4f}s")

with timer("sum"):
    sum(range(1_000_000))
```
""",
    "files": [
        lab("day03", "decorators.py", task=1),
        lab("day03", "generators.py", task=2),
        lab("day03", "contexts.py", task=3),
    ],
    "tasks": [
        "Read the Real Python guides on [decorators](https://realpython.com/primer-on-python-decorators/), [generators](https://realpython.com/introduction-to-python-generators/), and [the with statement](https://realpython.com/python-with-statement/)",
        "decorators.py: @timed and @retry(times=3)",
        "generators.py: compare memory of list vs generator on a 1M-row CSV",
        "contexts.py: class-based and @contextmanager timers; show cleanup on error",
        "Notes: when you'd use each one in an inference service",
        "GitHub: commit the [mmcows-visual](https://github.com/OussemaBouchaala/mmcows-visual) README",
    ],
    "done_when": "You can write all three from memory.",
    "resources": [
        {"label": "Real Python: decorators", "url": "https://realpython.com/primer-on-python-decorators/"},
        {"label": "Real Python: generators", "url": "https://realpython.com/introduction-to-python-generators/"},
        {"label": "Real Python: the with statement", "url": "https://realpython.com/python-with-statement/"},
        {"label": "Exercism Python track", "url": "https://exercism.org/tracks/python"},
    ],
    "quiz": [
        {"q": "What does functools.wraps preserve?", "options": ["The function's speed", "The wrapped function's name and docstring", "The return value", "Thread safety"], "answer": 1,
         "explain": "Without it, the decorated function reports the wrapper's name and docstring."},
        {"q": "Why is sum(x*x for x in range(10**7)) lighter on memory than sum([x*x for x in range(10**7)])?", "options": ["Generators are compiled", "The generator never builds the full list", "sum is faster on generators", "It isn't lighter"], "answer": 1,
         "explain": "The list comprehension materializes 10 million items; the generator yields them one at a time."},
        {"q": "In a @contextmanager, code in `finally` after `yield` runs...", "options": ["Only if no exception occurs", "Even if the with-block raises", "Never", "Only in a class-based manager"], "answer": 1,
         "explain": "That's the point of try/finally: cleanup always runs."},
    ],
}

DAY4 = {
    "id": "w1d4", "folder": "day04", "notes_task": 3, "date": "2026-10-08", "weekday": "Thu",
    "title": "Overfitting, bias and variance", "minutes": 75,
    "why": "You missed Q3. Read the train/validation gap, not the absolute scores.",
    "lesson": """
## Two ways a model fails

- **High bias (underfitting):** the model is too simple. Train and validation errors are both high and close together.
- **High variance (overfitting):** the model memorizes the training set. Train error is low, validation error is much higher.

The gap between train and validation tells you which one you have.

## Seeing it with polynomials

```python
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
```

Degree 1 misses the shape (bias). Degree 15 chases the noise (variance).

## Remedies, in order

For **variance**: get more data or augment it, add regularization (L2, dropout, max_depth), simplify the model, stop early.
For **bias**: add capacity or better features, reduce regularization, train longer.

## Learning curves

Plot train and validation scores as the training set grows. If validation keeps rising toward train, more data will help (variance). If both plateau low and close together, more data won't help (bias).
""",
    "files": [
        lab("day04", "poly_fit.py", task=1),
        lab("day04", "learning_curves.py", task=2),
    ],
    "tasks": [
        "Read the [ML Crash Course overfitting module](https://developers.google.com/machine-learning/crash-course/overfitting) and watch [StatQuest on bias and variance](https://www.youtube.com/watch?v=EuBBz3bI-aA)",
        "poly_fit.py: train vs validation MSE for degrees 1-15, plotted",
        "learning_curves.py: unlimited vs max_depth=3 tree",
        "Notes: given train 99% / val 72%, list the diagnosis and three remedies in order",
    ],
    "done_when": "You can look at a learning curve and say 'bias' or 'variance' with a reason.",
    "resources": [
        {"label": "Google ML Crash Course", "url": "https://developers.google.com/machine-learning/crash-course"},
        {"label": "MLU-Explain: bias-variance (interactive)", "url": "https://mlu-explain.github.io"},
    ],
    "quiz": [
        {"q": "Degree-15 polynomial on 20 points: tiny train error, large validation error. Diagnosis?", "options": ["High bias", "High variance", "Data leakage", "Perfect fit"], "answer": 1,
         "explain": "The large gap means it memorized the training noise."},
        {"q": "Train and validation errors are both high and close. Best first move?", "options": ["Add regularization", "Get more data", "Add capacity or better features", "Stop training earlier"], "answer": 2,
         "explain": "That's underfitting; the model needs to express more."},
        {"q": "Which does NOT reduce variance?", "options": ["More training data", "L2 regularization", "Raising the polynomial degree", "Early stopping"], "answer": 2,
         "explain": "Higher degree adds capacity, which increases variance."},
    ],
}

DAY5 = {
    "id": "w1d5", "folder": "day05", "notes_task": 3, "date": "2026-10-09", "weekday": "Fri",
    "title": "Metrics for imbalanced data", "minutes": 75,
    "why": "You missed Q4. The MmCows Drinking class (F1 around 0.05) is the same problem in your own work.",
    "lesson": """
## The accuracy trap

With 0.5% positives, a model that always says "negative" scores 99.5% accuracy and catches nothing.

## The metrics that matter

- **Precision** = TP / (TP + FP): of what I flagged, how much was right?
- **Recall** = TP / (TP + FN): of all real positives, how many did I catch?
- **F1** = 2PR / (P + R): balances both; low if either is low.
- **PR-AUC** summarizes precision vs recall across thresholds and focuses on the positive class.
- **ROC-AUC** uses the false positive rate, whose denominator is the huge negative class, so it can look good even when the positives are handled badly.

```python
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score

y_true = np.array([0] * 995 + [1] * 5)
y_pred = np.zeros(1000, dtype=int)
print("accuracy", accuracy_score(y_true, y_pred))
print("recall", recall_score(y_true, y_pred))
print("f1", f1_score(y_true, y_pred, zero_division=0))
```

## Thresholds are a choice

Classifiers output probabilities; 0.5 is just a default. Raising the threshold usually raises precision and lowers recall. Pick it from the cost of each error: missing fraud costs more than a false alarm.
""",
    "files": [
        lab("day05", "imbalance.py", task=1),
        lab("day05", "threshold.py", task=2),
    ],
    "tasks": [
        "Read the [scikit-learn model evaluation guide](https://scikit-learn.org/stable/modules/model_evaluation.html); watch [StatQuest on ROC and AUC](https://www.youtube.com/watch?v=4jRBRDbJemM)",
        "imbalance.py: dummy vs logistic regression on 0.5% positives",
        "threshold.py: precision-recall curve and a threshold for recall >= 0.8",
        "Notes: why accuracy and even ROC-AUC can look good on a useless model",
        "PFE: start a list of 15-20 target hosts (search [LinkedIn Jobs](https://www.linkedin.com/jobs/search/?keywords=PFE%20machine%20learning&location=Tunisia))",
    ],
    "done_when": "You can pick the right metric for fraud detection and defend it.",
    "resources": [
        {"label": "scikit-learn: model evaluation", "url": "https://scikit-learn.org/stable/modules/model_evaluation.html"},
        {"label": "MLU-Explain: precision & recall, ROC & AUC", "url": "https://mlu-explain.github.io"},
    ],
    "quiz": [
        {"q": "0.5% positives, model predicts all negative. Accuracy and recall?", "options": ["99.5%, 0", "50%, 0.5", "99.5%, 1.0", "0.5%, 0"], "answer": 0,
         "explain": "It's right on every negative and catches no positives."},
        {"q": "Raising the decision threshold usually...", "options": ["Raises recall, lowers precision", "Raises precision, lowers recall", "Raises both", "Changes neither"], "answer": 1,
         "explain": "You flag fewer cases, more confidently: fewer false alarms, more misses."},
        {"q": "Why prefer PR-AUC over ROC-AUC when positives are rare?", "options": ["It's faster to compute", "ROC's false positive rate is diluted by the huge negative class", "ROC-AUC needs balanced classes to compute", "PR-AUC is always higher"], "answer": 1,
         "explain": "Thousands of false positives barely move FPR when negatives number in the millions; precision shows them."},
    ],
}

DAY6 = {
    "id": "w1d6", "folder": "day06", "date": "2026-10-10", "weekday": "Sat",
    "title": "Data leakage and Pipelines", "minutes": 180,
    "why": "You missed Q5, and your team's sensor chapter fixed exactly this bug in the MmCows baseline.",
    "lesson": """
## What leakage is

Leakage is any information from the evaluation data, or from the future, reaching the model during training. Scores look great offline and collapse in production.

## Preprocessing leakage

Fitting a scaler, imputer, encoder, feature selector, or SMOTE on the full dataset lets test statistics shape training. Fit them on training data only.

```python
from sklearn.datasets import make_classification
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
import numpy as np

rng = np.random.default_rng(0)
X = rng.normal(size=(100, 5000))   # pure noise
y = rng.integers(0, 2, 100)

X_sel = SelectKBest(f_classif, k=20).fit_transform(X, y)   # leaks!
print("leaky:", cross_val_score(LogisticRegression(max_iter=1000), X_sel, y, cv=5).mean())

pipe = make_pipeline(SelectKBest(f_classif, k=20), LogisticRegression(max_iter=1000))
print("honest:", cross_val_score(pipe, X, y, cv=5).mean())
```

On pure noise, the leaky version looks like it learned something. The pipeline shows the truth: about 50%.

## Target leakage

A feature that is only known after, or because of, the label. Example: predicting loan default with "account sent to collections".

## The fix: Pipelines

Put every fitted step inside a `Pipeline` and pass the pipeline to cross-validation. Each fold then fits preprocessing on its own training part only. For SMOTE, use `imblearn.pipeline.Pipeline`.
""",
    "files": [
        lab("day06", "leakage_scaler.py", task=1),
        lab("day06", "target_leakage.py", task=2),
    ],
    "tasks": [
        "Read scikit-learn's [Common pitfalls page (data leakage section)](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage)",
        "leakage_scaler.py: leaky vs Pipeline, for a scaler and for SelectKBest",
        "target_leakage.py: show and explain target leakage",
        "Rewrite your [Real Estate](https://github.com/OussemaBouchaala/Appartments_Price_Prediction_Model) or [Fake Reviews](https://github.com/OussemaBouchaala/Fake_Real_Reviews_Classifier) notebook with all preprocessing in a Pipeline; push it",
        "GitHub: [update bio](https://github.com/settings/profile), [re-pin repos](https://github.com/OussemaBouchaala), re-save [ECG README](https://github.com/OussemaBouchaala/PPP_ECG_Signal_Classification) as UTF-8, handle mawkoutan",
        "Optional: [Kaggle Learn Intermediate ML](https://www.kaggle.com/learn/intermediate-machine-learning), Pipelines and Data Leakage lessons",
    ],
    "done_when": "Your old notebook has no preprocessing outside a Pipeline.",
    "resources": [
        {"label": "scikit-learn: Common pitfalls", "url": "https://scikit-learn.org/stable/common_pitfalls.html"},
        {"label": "Kaggle Learn: Intermediate ML", "url": "https://www.kaggle.com/learn/intermediate-machine-learning"},
    ],
    "quiz": [
        {"q": "Correct way to scale features in cross-validation?", "options": ["Scale the full dataset, then cross-validate", "Put scaler + model in a Pipeline passed to cross_val_score", "Scale only the test folds", "Skip scaling"], "answer": 1,
         "explain": "The pipeline refits the scaler on each fold's training part."},
        {"q": "Which feature is target leakage when predicting loan default?", "options": ["Applicant income", "Loan amount", "Account sent to collections", "Employment length"], "answer": 2,
         "explain": "Collections happen because of default, so the feature isn't available at prediction time."},
        {"q": "Your team found the MmCows baseline fitted the scaler separately on each split. The fix:", "options": ["Fit on all data at once", "Fit on train only, then transform val and test", "Fit on test only", "Remove scaling entirely"], "answer": 1,
         "explain": "Validation and test must be transformed with statistics learned from training data."},
    ],
}

DAY7 = {
    "id": "w1d7", "folder": "day07", "retest_task": 3, "date": "2026-10-11", "weekday": "Sun",
    "title": "Temporal cross-validation and re-test", "minutes": 180,
    "why": "You missed Q6, and your headline CV result (the 51% overestimate) is a temporal-CV result.",
    "lesson": """
## Why random splits lie on time series

Neighboring time steps are nearly identical. A random split puts near-duplicates in both train and test, so the model scores well by memorizing, not generalizing. In production it must predict the future from the past.

## Forward-chaining splits

`TimeSeriesSplit` trains on earlier data and validates on later data, fold after fold.

```python
import numpy as np
from sklearn.model_selection import TimeSeriesSplit

X = np.arange(12).reshape(-1, 1)
for train, test in TimeSeriesSplit(n_splits=3).split(X):
    print("train", train, "test", test)
```

## Group splits

When the question is "does it work on a new cow, patient, or user?", keep every sample of a group on one side with `GroupKFold`.

## Your MmCows result, explained

The naive 70/15/15 split put frames seconds apart into train and test. Those frames show the same cow in nearly the same place and posture, so the 17-class YOLO "recognized" cows by memorizing positions. Testing on a separate 2-hour period with different lighting removed that shortcut: mAP@0.5 fell from 0.987 to 0.481. That's the answer you need to give fluently in interviews.
""",
    "files": [
        lab("day07", "temporal_cv.py", task=1),
    ],
    "tasks": [
        "Read the [scikit-learn cross-validation guide](https://scikit-learn.org/stable/modules/cross_validation.html#cross-validation-of-time-series-data) (TimeSeriesSplit, GroupKFold)",
        "temporal_cv.py: shuffled KFold vs TimeSeriesSplit on an autocorrelated series",
        "Write and record a 2-minute explanation of the 51% MmCows overestimate",
        "Beat the Week 1 boss: the re-test after the quiz (target 8/10)",
        "Weekly retro: tick the tracker; [send Claude](https://claude.ai) your progress for Week 3's plan",
    ],
    "done_when": "8/10 on the re-test. Below 8: redo the missed topics on Mon-Tue of Week 2.",
    "resources": [
        {"label": "scikit-learn: cross-validation", "url": "https://scikit-learn.org/stable/modules/cross_validation.html#time-series-split"},
        {"label": "MLU-Explain: cross-validation", "url": "https://mlu-explain.github.io"},
    ],
    "quiz": [
        {"q": "What does TimeSeriesSplit guarantee?", "options": ["Balanced classes per fold", "Each fold trains on earlier data and tests on later data", "Random shuffling", "Equal-size train sets"], "answer": 1,
         "explain": "Forward-chaining mirrors how the model is used: predict the future from the past."},
        {"q": "You need to know if a model works on cows it has never seen. Which splitter?", "options": ["KFold(shuffle=True)", "StratifiedKFold", "GroupKFold by cow id", "TimeSeriesSplit"], "answer": 2,
         "explain": "Grouping keeps each cow entirely in train or entirely in test."},
        {"q": "Why did the naive MmCows split overestimate mAP@0.5 by 51%?", "options": ["The model was too small", "Near-identical neighboring frames appeared in both train and test", "The test set had more cows", "Bad annotation quality"], "answer": 1,
         "explain": "The model memorized positions and postures from adjacent frames instead of learning identity."},
    ],
    "retest": [
        {"q": "What does this print?\nfns = [lambda: i for i in range(3)]\nprint([f() for f in fns])", "options": ["[0, 1, 2]", "[2, 2, 2]", "[0, 0, 0]", "NameError"], "answer": 1,
         "explain": "Closures look up i when called, not when created; by then the loop left i = 2. Fix: lambda i=i: i."},
        {"q": "What happens?\nx = (1, [2])\nx[1] += [3]", "options": ["x becomes (1, [2, 3]), no error", "TypeError, and x stays (1, [2])", "TypeError, but x becomes (1, [2, 3])", "x becomes (1, [2], [3])"], "answer": 2,
         "explain": "+= mutates the list in place first, then tries to assign into the tuple, which fails."},
        {"q": "An async def endpoint calls requests.get(slow_url). Which is NOT a fix?", "options": ["Use httpx.AsyncClient with await", "Declare the endpoint with plain def", "Write `await requests.get(slow_url)`", "Wrap the call with run_in_threadpool"], "answer": 2,
         "explain": "requests.get isn't awaitable; await on it raises a TypeError."},
        {"q": "await asyncio.gather(a(), b(), c()), each doing await asyncio.sleep(1). Total time?", "options": ["About 1s", "About 3s", "About 0s", "Depends on CPU cores"], "answer": 0,
         "explain": "The waits overlap on the event loop."},
        {"q": "What does this print?\ng = (x for x in range(3))\nprint(list(g), list(g))", "options": ["[0, 1, 2] [0, 1, 2]", "[0, 1, 2] []", "[] []", "TypeError"], "answer": 1,
         "explain": "A generator is exhausted after one pass."},
        {"q": "Learning curve: as data grows, train score falls and validation rises; both meet at a low value. More data will...", "options": ["Help a lot", "Barely help: the model has high bias", "Cause overfitting", "Raise the train score"], "answer": 1,
         "explain": "Converged low curves mean the model lacks capacity."},
        {"q": "Precision 0.9 and recall 0.1. F1?", "options": ["0.50", "0.18", "0.90", "0.10"], "answer": 1,
         "explain": "2 x 0.9 x 0.1 / (0.9 + 0.1) = 0.18. F1 punishes the weak side."},
        {"q": "Where does SMOTE belong in cross-validation?", "options": ["On the full dataset before splitting", "Inside the pipeline, applied to training folds only", "On the test set", "After evaluation"], "answer": 1,
         "explain": "Oversampling before the split leaks synthetic copies of test points into training."},
        {"q": "You select the top 20 of 5,000 features using all data, then cross-validate. The score is...", "options": ["Honest", "Optimistic: selection saw the validation folds", "Pessimistic", "Unaffected"], "answer": 1,
         "explain": "Selection must happen inside each fold, like any fitted step."},
        {"q": "Daily sales 2020-2025; you'll forecast 2026. Best validation?", "options": ["Random 80/20 split", "Train on 2020-2024, validate on 2025", "Validate on 2020, train on the rest", "Leave-one-out"], "answer": 1,
         "explain": "Validate the way you'll deploy: past to train, the most recent period to test."},
    ],
}

WEEK1 = {
    "n": 1, "phase": "Phase 0", "title": "Fundamentals + GitHub", "dates": "Oct 5-11",
    "goal": "Close the gaps from the 4/10 test and publish the new READMEs.",
    "gate": "8/10 on the re-test",
    "days": [DAY1, DAY2, DAY3, DAY4, DAY5, DAY6, DAY7],
}
