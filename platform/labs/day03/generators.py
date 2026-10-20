# Compare memory: read everything into a list vs stream rows with a generator.
import csv
import os
import tracemalloc

CSV_PATH = "big.csv"
N_ROWS = 1_000_000


def write_csv(path=CSV_PATH, n_rows=N_ROWS):
    """Write a CSV with the header `id,value`, then n_rows rows where value = id % 100."""
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        # TODO: write the header row, then the n_rows data rows
        ...


def sum_with_list(path=CSV_PATH):
    """Read ALL rows into a list first (list(csv.DictReader(f))), then sum int(row["value"])."""
    # TODO
    ...


def read_rows(path=CSV_PATH):
    """Generator: open the file and `yield` one row (a dict) at a time."""
    # TODO: use `yield` inside the with-block
    ...


def sum_with_generator(path=CSV_PATH):
    """Same sum as sum_with_list, but iterate over read_rows() so no list is built."""
    # TODO
    ...


def peak_memory(fn, *args):
    """Run fn(*args) and return (result, peak bytes allocated while it ran)."""
    tracemalloc.start()
    result = fn(*args)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, peak


if __name__ == "__main__":
    if not os.path.exists(CSV_PATH):
        write_csv()
    for f in (sum_with_list, sum_with_generator):
        total, peak = peak_memory(f)
        print(f"{f.__name__:<20} total={total}  peak={peak / 1e6:.1f} MB")
