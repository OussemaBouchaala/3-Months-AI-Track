# 1. Write @timed from memory (use functools.wraps). Apply it to two functions.
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
def loop():
    for i in range(1000):
        continue
@timed 
def loop2():
    i=0
    while (i<1000):
        i+=1
# 2. Write @retry(times=3) that retries a function when it raises.
#    Hint: a decorator WITH arguments needs one more level of nesting.
def retry(times=3, delay=0):
    """Decorator that retries a function up to `times` when it raises an exception."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == times:
                        # Re-raise the exception on the final attempt
                        raise e
                    if delay > 0:
                        time.sleep(delay)
        return wrapper
    return decorator
import random

@retry(times=3)
def unstable_api_call():
    print("Attempting request...")
    if random.random() < 0.7:
        raise ConnectionError("Network flaked!")
    return "Success!"

# Test the wrapped function
try:
    result = unstable_api_call()
    print(result)
except ConnectionError:
    print("Failed after 3 attempts.")
    
    