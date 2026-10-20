# Part A: reproduce and fix the mutable default bug.
# Fill in the four function bodies (replace each `...`).
# Write your prediction in the yellow box, press Run, then press Check.


def add_buggy(x, items=[]):
    """Append x to items and return items.
    Keep `items=[]` as the default: this version has the bug on purpose."""
    ...


def add_fixed(x, items=None):
    """Same job as add_buggy, but every call WITHOUT items gets its own new list.
    Pattern: if items is None: items = []"""
    ...


def log_request_buggy(user_id, history=[]):
    """A 'server' helper with the bug: append user_id to history and return history."""
    ...


def log_request(user_id, history=None):
    """Fixed version: a request that passes no history starts from an empty list."""
    ...


if __name__ == "__main__":
    # 1. Three calls to the buggy version. Watch add_buggy.__defaults__ change.
    for x in (1, 2, 3):
        print(add_buggy(x), add_buggy.__defaults__)

    # 2. The fixed version: three independent lists.
    print(add_fixed(1), add_fixed(2), add_fixed(3))

    # 3. Three 'requests' from different users: buggy, then fixed.
    print([log_request_buggy(user) for user in ("alice", "bob", "carol")])
    print([log_request(user) for user in ("alice", "bob", "carol")])
