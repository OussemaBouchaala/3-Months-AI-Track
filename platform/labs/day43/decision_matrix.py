# Phase 2 starts: pick ONE project for the next 6 weeks, with a weighted decision matrix
# instead of a gut feeling. Then check the winner survives small changes to the weights.

CRITERIA = {                 # weight: how much each criterion matters to YOU (any positive numbers)
    "real_user": 3,          # a real person will use it and talk to you
    "data_access": 3,        # you can get the documents within a week
    "arabic": 2,             # uses the Arabic skills from Phase 1
    "action": 2,             # has at least one real action (tool) to perform
    "demo": 1,               # easy to show in a 3-5 minute video
}

OPTIONS = {                  # score each option 1-5 on each criterion (edit with your real options)
    "Agency document assistant": {"real_user": 4, "data_access": 4, "arabic": 4, "action": 5, "demo": 4},
    "Contract clause extractor": {"real_user": 3, "data_access": 2, "arabic": 3, "action": 2, "demo": 3},
    "Support chatbot for a shop": {"real_user": 3, "data_access": 3, "arabic": 3, "action": 4, "demo": 5},
}


def normalize_weights(criteria):
    """Weights scaled to sum to 1, same keys. Raise ValueError if any weight is negative or all are 0."""
    # TODO
    ...


def weighted_score(scores, weights):
    """sum(weight * score) over the criteria in weights. A criterion missing from scores raises KeyError."""
    # TODO
    ...


def rank(options, criteria):
    """[(name, score), ...] sorted best first, score rounded to 2 decimals. Ties: alphabetical by name."""
    # TODO
    ...


def sensitivity(options, criteria, delta=1):
    """For each criterion, raise its weight by delta, then lower it by delta (not below 0), and re-rank.
    Return the sorted list of criteria for which the winner changes in either direction. [] = robust choice."""
    # TODO
    ...


if __name__ == "__main__":
    for name, score in rank(OPTIONS, CRITERIA):
        print(f"{score:5.2f}  {name}")
    print("winner changes if you move:", sensitivity(OPTIONS, CRITERIA) or "nothing (robust)")
