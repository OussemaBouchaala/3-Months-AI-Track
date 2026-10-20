# List vs generator memory
**Topic:** a generator yields one value at a time and never builds the whole list.

## Your mission
Sum one column of a 1,000,000-row CSV two ways and compare peak memory.

## Steps
1. `write_csv`: header `id,value`, then rows `[i, i % 100]`.
2. `sum_with_list`: `list(csv.DictReader(f))`, then sum.
3. `read_rows`: `yield` rows from inside the `with` block.
4. `sum_with_generator`: sum over `read_rows(path)`.
5. **Run** and compare the two peaks printed by `peak_memory`.

## Done when
**Check** shows the same total and a much smaller peak for the generator.
