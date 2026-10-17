# Part A: reproduce and fix the mutable default bug
# For each step, write your PREDICTION in the yellow box before running.

# 1. Write add(x, items=[]). Call it three times, print each result,
#    and print add.__defaults__ after each call.
def add(x,items=[]):
    items.append(x)
    return items
print(add(1),add.__defaults__)
print(add(2),add.__defaults__)
print(add(5),add.__defaults__)
# 2. Write the fixed version (items=None) and show three independent lists.
def add(x, items=None):
    if items is None:
        items=[]
    items.append(x)
    return items
print(add(1), add(2) ,add(3))
# 3. Realistic bug: log_request(user_id, history=[]) appends user_id and returns history.
#    Simulate 3 requests from different users, show the leak, then fix it.
def log_request(user_id, history=[]):
    history.append(user_id)
    return history
user1=log_request(1)
user2=log_request(2)
user3=log_request(3)
print(user1,user2,user3)
# Fix: make requests chained 
def log_request(user_id, history=None):
    if history is None:
        history=[]
    history.append(user_id)
    return history
user1=log_request(1)
user2=log_request(2)
user3=log_request(3)
print(user1,user2,user3)
