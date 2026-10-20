import inspect
import os
import tempfile
import tracemalloc

tmp = tempfile.mkdtemp()
small = os.path.join(tmp, "small.csv")
fn("write_csv")(small, 1000)
expected = sum(i % 100 for i in range(1000))


def lines():
    with open(small) as f:
        return f.read().splitlines()


check("write_csv writes a header and n rows", lambda: len(lines()) == 1001 and lines()[0].replace(" ", "") == "id,value",
      "First writer.writerow(['id', 'value']), then one row per id.")
check("each row is id, id % 100", lambda: lines()[1:3] == ["0,0", "1,1"] and lines()[101] == "100,0")
check("sum_with_list returns the right total", lambda: fn("sum_with_list")(small) == expected,
      f"Expected {expected} for 1,000 rows. Convert with int(row['value']).")
check("read_rows is a generator function (uses yield)", lambda: inspect.isgeneratorfunction(fn("read_rows")))
check("read_rows yields one row per data line", lambda: sum(1 for _ in fn("read_rows")(small)) == 1000)
check("sum_with_generator returns the same total", lambda: fn("sum_with_generator")(small) == expected)

medium = os.path.join(tmp, "medium.csv")
fn("write_csv")(medium, 50_000)


def peak(f):
    tracemalloc.start()
    f(medium)
    p = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    return p


check("the generator version uses far less memory than the list version",
      lambda: peak(fn("sum_with_generator")) * 5 < peak(fn("sum_with_list")),
      "sum_with_generator must not build a list: sum(int(r['value']) for r in read_rows(path)).")
