IDK = "I don't know based on the documents."
cases = [([], IDK), ([], "Yes, we sell cars."), (["c6"], IDK)]
for source_ids, answer in cases:
    if not source_ids:
        print("unanswerable ->", "correct" if IDK in answer else "invented!")
    elif IDK in answer:
        print("answerable ->", "false IDK")
