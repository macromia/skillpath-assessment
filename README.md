# Assessment

## Scenario: Retail Analytics Mini‑Pipeline

>You’ve joined **Acme Retail** as a junior software developer. Your first task is to build a tiny analytics pipeline that reads a CSV of e‑commerce orders, performs some calculations, and writes results for a business analyst to review.

### Input

A CSV file with a header row. Fields:

* `order_id` (string)
* `customer_id` (string)
* `category` (string)
* `unit_price` (decimal)
* `quantity` (integer)
* `timestamp` (ISO 8601 string)

**Example** (`orders.csv`):

```
order_id,customer_id,category,unit_price,quantity,timestamp
O-1001,C-001,Books,12.99,2,2025-03-01T10:15:00Z
O-1002,C-002,Electronics,199.99,1,2025-03-02T12:00:00Z
O-1003,C-003,Toys,9.50,5,2025-03-02T14:20:00Z
```

### What you must build

Implement a small program (in **Python or Java**) that:

1. **Parses orders** from the CSV into an **`Order` class** (OOP) with private fields, constructor, and getters; include a method `total()` that returns `unit_price * quantity`.
2. **Aggregates analytics**:

   * `total_revenue` (sum of all `total()`)
   * `average_order_value` (mean of `total()`; 2 decimal places)
   * `orders_per_category` (dictionary/map of category → count)
   * `top_category_by_revenue` (category with highest revenue; ties broken by alphabetical order)
3. **Filters high‑value orders**: take a numeric threshold (e.g., `>= 100.00`) and produce a list of orders meeting or exceeding it.
4. **Writes two outputs**:

   * `summary.json` with the aggregate analytics:

     ```json
     {
       "total_revenue": 231.98,
       "average_order_value": 77.33,
       "orders_per_category": {"Books": 1, "Electronics": 1, "Toys": 1},
       "top_category_by_revenue": "Electronics"
     }
     ```
   * `high_value_orders.csv` (same columns as input, but **only** high‑value rows).
5. **CLI/Args**: Program accepts 2 arguments: `--input <path>` and `--threshold <number>`; default threshold is **100.0** if not provided.
6. **Exception handling**: Robustly handle nonexistent files, malformed numbers, and missing columns. Do not crash; print/log a readable message and exit with a non‑zero status if input is unrecoverable.
7. **Unit tests**: Provide at least **two** tests that exercise `Order.total()` and the filtering/aggregation logic.

### Output Files

* `summary.json`
* `high_value_orders.csv`

### Constraints & Tips

* You **must** use **functions/methods** with parameters and return values.
* Use **conditionals/loops** appropriately (e.g., iterating rows, computing aggregates).
* Use **file I/O** to read CSV and write JSON/CSV outputs.
* Use **try/except** (Python) or **try/catch** (Java) for error handling.
* Use **OOP** via an `Order` class with encapsulation.
* Provide **unit tests** (`unittest` for Python, `JUnit` for Java).

### Starter Code (optional)

You may start from these minimal stubs.

##### Python

[models.py](starter-code/python/models.py)

[process_orders.py](starter-code/python/process_orders.py)

##### Java

[Order.java](starter-code/java/Order.java)

[OrderProcessor.java](starter-code/java/OrderProcessor.java)

# Auto‑Grading Rubric & Logic

| Skill Being Assessed                         | Auto‑Grading Check        | Logic for Verification / Criteria for Mastery                                                                                                                                                               |
| -------------------------------------------- | ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Implement & use functions/methods            | Static analysis + runtime | **Pass** if at least one non‑trivial function/method with parameters and a return value is defined **and** invoked (e.g., `aggregate`, `filter_high_value`, `total`).                                       |
| Apply control flow (conditionals/loops)      | Static analysis           | **Pass** if the submitted code includes at least one loop (`for`/`while` or stream loop in Java) **and** at least one conditional (`if`/`?:`) tied to core logic (e.g., filtering by threshold, tie‑break). |
| Read & write files                           | Black‑box run             | Run program with provided `orders.csv` and threshold; **Pass** if it reads the CSV and writes **both** `summary.json` and `high_value_orders.csv` with non‑empty, well‑formed contents.                     |
| Handle exceptions & edge cases               | Black‑box run + grep      | **Pass** if nonexistent input causes non‑zero exit and message; malformed rows do not crash execution and are skipped/logged.                                                                               |
| Apply OOP principles (class + encapsulation) | Static analysis           | **Pass** if an `Order` class exists with private fields (Java) or dataclass/attributes (Python), constructor, and a `total()` method used in computation.                                                   |
| Write & execute unit tests                   | Test runner               | **Pass** if at least **2** tests are present and pass (Python `unittest`, Java `JUnit`).                                                                                                                    |
## What to Submit

* Your source files (Python or Java).
* Your test files.
* The generated `summary.json` and `high_value_orders.csv` from running on the provided sample or grader’s dataset.

> **NOTE:** To run the autograder run `run_grader.py` (e.g. `python /workspaces/skillpath-assessment/autograder/run_grader.py --lang python`)


