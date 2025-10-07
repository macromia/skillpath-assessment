# Part 1 — Learner Problem Statement (with Starter Code)

## Scenario: Retail Analytics Mini‑Pipeline

You’ve joined **Acme Retail** as a junior software developer. Your first task is to build a tiny analytics pipeline that reads a CSV of e‑commerce orders, performs some calculations, and writes results for a business analyst to review.

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
* Optional: `run.log` of any warnings/errors you choose to log.

### Constraints & Tips

* You **must** use **functions/methods** with parameters and return values.
* Use **conditionals/loops** appropriately (e.g., iterating rows, computing aggregates).
* Use **file I/O** to read CSV and write JSON/CSV outputs.
* Use **try/except** (Python) or **try/catch** (Java) for error handling.
* Use **OOP** via an `Order` class with encapsulation.
* Provide **unit tests** (`unittest` for Python, `JUnit` for Java).

### Starter Code (optional)

You may start from these minimal stubs.

#### Python — `models.py`

```python
from dataclasses import dataclass

@dataclass
class Order:
    order_id: str
    customer_id: str
    category: str
    unit_price: float
    quantity: int
    timestamp: str

    def total(self) -> float:
        # TODO: return unit_price * quantity
        raise NotImplementedError
```

#### Python — `process_orders.py`

```python
import argparse

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--input', required=True)
    p.add_argument('--threshold', type=float, default=100.0)
    return p.parse_args()

if __name__ == '__main__':
    args = parse_args()
    # TODO: read CSV, build Order objects, compute analytics, write outputs
```

#### Java — `Order.java`

```java
public class Order {
    // TODO: private fields, constructor, getters, total()
}
```

#### Java — `OrderProcessor.java`

```java
public class OrderProcessor {
    public static void main(String[] args) {
        // TODO: parse --input and --threshold, read CSV, compute analytics, write outputs
    }
}
```

---

# Part 2 — Complete & Correct Solution (Answer Key)

> The following reference implementations satisfy all requirements and can be used for auto‑grading.

## Python Solution

### `models.py`

```python
from dataclasses import dataclass

@dataclass
class Order:
    order_id: str
    customer_id: str
    category: str
    unit_price: float
    quantity: int
    timestamp: str

    def total(self) -> float:
        return round(self.unit_price * self.quantity, 2)
```

### `process_orders.py`

```python
import argparse
import csv
import json
import logging
import math
import sys
from typing import List, Dict
from models import Order

logging.basicConfig(filename='run.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

REQUIRED_COLUMNS = [
    'order_id', 'customer_id', 'category', 'unit_price', 'quantity', 'timestamp'
]


def parse_args():
    p = argparse.ArgumentParser(description='Retail analytics mini-pipeline')
    p.add_argument('--input', required=True, help='Path to orders CSV')
    p.add_argument('--threshold', type=float, default=100.0,
                   help='High-value threshold (default 100.0)')
    return p.parse_args()


def load_orders(path: str) -> List[Order]:
    orders: List[Order] = []
    try:
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
            if missing:
                raise ValueError(f'Missing columns: {missing}')
            for i, row in enumerate(reader, start=2):
                try:
                    unit_price = float(row['unit_price'])
                    quantity = int(row['quantity'])
                    orders.append(Order(
                        order_id=row['order_id'],
                        customer_id=row['customer_id'],
                        category=row['category'],
                        unit_price=unit_price,
                        quantity=quantity,
                        timestamp=row['timestamp']
                    ))
                except (KeyError, ValueError) as e:
                    logging.warning('Skipping malformed row %d: %s', i, e)
    except FileNotFoundError:
        logging.error('Input file not found: %s', path)
        raise
    return orders


def aggregate(orders: List[Order]) -> Dict:
    totals = [o.total() for o in orders]
    total_revenue = round(sum(totals), 2)
    avg = round(total_revenue / len(totals), 2) if totals else 0.0

    per_cat: Dict[str, int] = {}
    revenue_by_cat: Dict[str, float] = {}
    for o in orders:
        per_cat[o.category] = per_cat.get(o.category, 0) + 1
        revenue_by_cat[o.category] = revenue_by_cat.get(o.category, 0.0) + o.total()

    # Resolve ties alphabetically for determinism
    top_cat = None
    if revenue_by_cat:
        max_rev = max(revenue_by_cat.values())
        top_candidates = [c for c, r in revenue_by_cat.items() if math.isclose(r, max_rev, rel_tol=1e-9) or r == max_rev]
        top_cat = sorted(top_candidates)[0]

    return {
        'total_revenue': round(total_revenue, 2),
        'average_order_value': round(avg, 2),
        'orders_per_category': per_cat,
        'top_category_by_revenue': top_cat
    }


def filter_high_value(orders: List[Order], threshold: float) -> List[Order]:
    return [o for o in orders if o.total() >= threshold]


def write_summary(path: str, data: Dict) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def write_high_value_csv(path: str, rows: List[Order]) -> None:
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=REQUIRED_COLUMNS)
        writer.writeheader()
        for o in rows:
            writer.writerow({
                'order_id': o.order_id,
                'customer_id': o.customer_id,
                'category': o.category,
                'unit_price': f'{o.unit_price:.2f}',
                'quantity': o.quantity,
                'timestamp': o.timestamp,
            })


def main():
    args = parse_args()
    try:
        orders = load_orders(args.input)
        if not orders:
            logging.error('No valid orders found in %s', args.input)
            print('No valid orders found.', file=sys.stderr)
            sys.exit(2)
        summary = aggregate(orders)
        write_summary('summary.json', summary)
        hv = filter_high_value(orders, args.threshold)
        write_high_value_csv('high_value_orders.csv', hv)
        print('Wrote summary.json and high_value_orders.csv')
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
```

### `tests/test_orders.py`

```python
import unittest
from models import Order
from process_orders import aggregate, filter_high_value

class TestOrders(unittest.TestCase):
    def test_order_total(self):
        o = Order('O1','C1','Books',12.5,4,'2025-01-01T00:00:00Z')
        self.assertEqual(o.total(), 50.0)

    def test_aggregate_and_filter(self):
        orders = [
            Order('O1','C1','A',50.0,1,'t'),
            Order('O2','C2','B',20.0,3,'t'),
            Order('O3','C3','A',60.0,2,'t')
        ]
        summary = aggregate(orders)
        self.assertAlmostEqual(summary['total_revenue'], 50+60+40, places=2)
        self.assertEqual(summary['orders_per_category']['A'], 2)
        hv = filter_high_value(orders, 100.0)
        self.assertEqual(len(hv), 1)
        self.assertEqual(hv[0].order_id, 'O3')

if __name__ == '__main__':
    unittest.main()
```

---

## Java Solution

### `Order.java`

```java
import java.math.BigDecimal;

public class Order {
    private final String orderId;
    private final String customerId;
    private final String category;
    private final BigDecimal unitPrice;
    private final int quantity;
    private final String timestamp;

    public Order(String orderId, String customerId, String category,
                 BigDecimal unitPrice, int quantity, String timestamp) {
        this.orderId = orderId;
        this.customerId = customerId;
        this.category = category;
        this.unitPrice = unitPrice;
        this.quantity = quantity;
        this.timestamp = timestamp;
    }

    public String getOrderId() { return orderId; }
    public String getCustomerId() { return customerId; }
    public String getCategory() { return category; }
    public BigDecimal getUnitPrice() { return unitPrice; }
    public int getQuantity() { return quantity; }
    public String getTimestamp() { return timestamp; }

    public BigDecimal total() {
        return unitPrice.multiply(BigDecimal.valueOf(quantity)).setScale(2, BigDecimal.ROUND_HALF_UP);
    }
}
```

### `OrderProcessor.java`

```java
import java.io.*;
import java.math.BigDecimal;
import java.nio.file.*;
import java.util.*;
import java.util.stream.Collectors;

public class OrderProcessor {
    private static final String[] REQUIRED = new String[]{
            "order_id","customer_id","category","unit_price","quantity","timestamp"
    };

    public static void main(String[] args) {
        Map<String, String> argmap = parseArgs(args);
        String input = argmap.get("--input");
        if (input == null) {
            System.err.println("Missing --input");
            System.exit(1);
        }
        BigDecimal threshold = new BigDecimal(argmap.getOrDefault("--threshold", "100.0"));
        try {
            List<Order> orders = loadOrders(input);
            if (orders.isEmpty()) {
                System.err.println("No valid orders found.");
                System.exit(2);
            }
            Map<String, Object> summary = aggregate(orders);
            writeSummary("summary.json", summary);
            List<Order> hv = filterHighValue(orders, threshold);
            writeHighValueCsv("high_value_orders.csv", hv);
            System.out.println("Wrote summary.json and high_value_orders.csv");
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            System.exit(1);
        }
    }

    static Map<String, String> parseArgs(String[] args) {
        Map<String, String> m = new HashMap<>();
        for (int i = 0; i < args.length; i++) {
            if (args[i].startsWith("--")) {
                String key = args[i];
                String val = (i + 1 < args.length && !args[i+1].startsWith("--")) ? args[++i] : "true";
                m.put(key, val);
            }
        }
        return m;
    }

    static List<Order> loadOrders(String path) throws Exception {
        List<Order> out = new ArrayList<>();
        try (BufferedReader br = Files.newBufferedReader(Paths.get(path))) {
            String header = br.readLine();
            if (header == null) throw new IllegalArgumentException("Empty file");
            String[] cols = header.split(",");
            Set<String> set = new HashSet<>(Arrays.asList(cols));
            for (String req : REQUIRED) if (!set.contains(req))
                throw new IllegalArgumentException("Missing columns: " + req);
            String line; int row = 1;
            while ((line = br.readLine()) != null) {
                row++;
                String[] parts = line.split(",");
                try {
                    Map<String, String> r = mapRow(cols, parts);
                    BigDecimal unitPrice = new BigDecimal(r.get("unit_price"));
                    int quantity = Integer.parseInt(r.get("quantity"));
                    out.add(new Order(
                            r.get("order_id"), r.get("customer_id"), r.get("category"),
                            unitPrice, quantity, r.get("timestamp")
                    ));
                } catch (Exception ex) {
                    // skip malformed row
                }
            }
        }
        return out;
    }

    static Map<String, String> mapRow(String[] cols, String[] parts) {
        Map<String, String> r = new HashMap<>();
        for (int i = 0; i < Math.min(cols.length, parts.length); i++) {
            r.put(cols[i], parts[i]);
        }
        return r;
    }

    static Map<String, Object> aggregate(List<Order> orders) {
        double totalRevenue = orders.stream()
                .map(o -> o.total())
                .mapToDouble(bd -> bd.doubleValue())
                .sum();
        totalRevenue = Math.round(totalRevenue * 100.0) / 100.0;
        double aov = orders.isEmpty() ? 0.0 : Math.round((totalRevenue / orders.size()) * 100.0) / 100.0;

        Map<String, Long> perCat = orders.stream()
                .collect(Collectors.groupingBy(Order::getCategory, Collectors.counting()));

        Map<String, Double> revenueByCat = new HashMap<>();
        for (Order o : orders) {
            revenueByCat.merge(o.getCategory(), o.total().doubleValue(), Double::sum);
        }
        String topCat = null;
        if (!revenueByCat.isEmpty()) {
            double max = revenueByCat.values().stream().mapToDouble(Double::doubleValue).max().orElse(0);
            List<String> candidates = revenueByCat.entrySet().stream()
                    .filter(e -> Math.abs(e.getValue() - max) < 1e-9)
                    .map(Map.Entry::getKey).sorted().collect(Collectors.toList());
            topCat = candidates.get(0);
        }
        Map<String, Object> summary = new LinkedHashMap<>();
        summary.put("total_revenue", round2(totalRevenue));
        summary.put("average_order_value", round2(aov));
        summary.put("orders_per_category", perCat);
        summary.put("top_category_by_revenue", topCat);
        return summary;
    }

    static double round2(double d) {
        return Math.round(d * 100.0) / 100.0;
    }

    static List<Order> filterHighValue(List<Order> orders, BigDecimal threshold) {
        return orders.stream()
                .filter(o -> o.total().compareTo(threshold) >= 0)
                .collect(Collectors.toList());
    }

    static void writeSummary(String path, Map<String, Object> summary) throws IOException {
        try (Writer w = new BufferedWriter(new FileWriter(path))) {
            w.write("{\n");
            int i = 0; int n = summary.size();
            for (Map.Entry<String, Object> e : summary.entrySet()) {
                w.write(String.format("  \"%s\": %s%s\n", e.getKey(), jsonValue(e.getValue()), (++i<n)?",":""));
            }
            w.write("}\n");
        }
    }

    static String jsonValue(Object v) {
        if (v == null) return "null";
        if (v instanceof String) return \"\" + v.toString().replace("\"", "\\\"") + \"\";
        if (v instanceof Number) return v.toString();
        if (v instanceof Map) {
            @SuppressWarnings("unchecked") Map<String, Object> m = (Map<String, Object>) v;
            StringBuilder sb = new StringBuilder("{");
            int i=0; int n=m.size();
            for (Map.Entry<String,Object> e : m.entrySet()) {
                sb.append("\""+e.getKey()+"\": "+jsonValue(e.getValue()));
                if (++i<n) sb.append(", ");
            }
            sb.append("}");
            return sb.toString();
        }
        if (v instanceof Iterable) {
            StringBuilder sb = new StringBuilder("[");
            Iterator<?> it = ((Iterable<?>) v).iterator();
            while (it.hasNext()) { sb.append(jsonValue(it.next())); if (it.hasNext()) sb.append(", "); }
            sb.append("]");
            return sb.toString();
        }
        return \"\" + v.toString() + \"\";
    }

    static void writeHighValueCsv(String path, List<Order> rows) throws IOException {
        try (BufferedWriter bw = Files.newBufferedWriter(Paths.get(path))) {
            bw.write(String.join(",", REQUIRED));
            bw.newLine();
            for (Order o : rows) {
                bw.write(String.format("%s,%s,%s,%.2f,%d,%s",
                        o.getOrderId(), o.getCustomerId(), o.getCategory(),
                        o.getUnitPrice(), o.getQuantity(), o.getTimestamp()));
                bw.newLine();
            }
        }
    }
}
```

### `OrderTest.java` (JUnit 4)

```java
import org.junit.Test;
import static org.junit.Assert.*;
import java.math.BigDecimal;
import java.util.*;

public class OrderTest {
    @Test
    public void testOrderTotal() {
        Order o = new Order("O1","C1","Books", new BigDecimal("12.50"), 4, "t");
        assertEquals(new BigDecimal("50.00"), o.total());
    }

    @Test
    public void testAggregateAndFilter() {
        List<Order> orders = Arrays.asList(
            new Order("O1","C1","A", new BigDecimal("50.0"),1,"t"),
            new Order("O2","C2","B", new BigDecimal("20.0"),3,"t"),
            new Order("O3","C3","A", new BigDecimal("60.0"),2,"t")
        );
        Map<String,Object> summary = OrderProcessor.aggregate(orders);
        assertEquals(150.00, (Double) summary.get("total_revenue"), 0.001);
        @SuppressWarnings("unchecked") Map<String, Long> perCat = (Map<String, Long>) summary.get("orders_per_category");
        assertEquals(Long.valueOf(2L), perCat.get("A"));
        List<Order> hv = OrderProcessor.filterHighValue(orders, new BigDecimal("100.0"));
        assertEquals(1, hv.size());
        assertEquals("O3", hv.get(0).getOrderId());
    }
}
```

---

# Part 3 — Auto‑Grading Rubric & Logic

| Skill Being Assessed                         | Auto‑Grading Check        | Logic for Verification / Criteria for Mastery                                                                                                                                                               |
| -------------------------------------------- | ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Implement & use functions/methods            | Static analysis + runtime | **Pass** if at least one non‑trivial function/method with parameters and a return value is defined **and** invoked (e.g., `aggregate`, `filter_high_value`, `total`).                                       |
| Apply control flow (conditionals/loops)      | Static analysis           | **Pass** if the submitted code includes at least one loop (`for`/`while` or stream loop in Java) **and** at least one conditional (`if`/`?:`) tied to core logic (e.g., filtering by threshold, tie‑break). |
| Read & write files                           | Black‑box run             | Run program with provided `orders.csv` and threshold; **Pass** if it reads the CSV and writes **both** `summary.json` and `high_value_orders.csv` with non‑empty, well‑formed contents.                     |
| Handle exceptions & edge cases               | Black‑box run + grep      | **Pass** if nonexistent input causes non‑zero exit and message; malformed rows do not crash execution and are skipped/logged.                                                                               |
| Apply OOP principles (class + encapsulation) | Static analysis           | **Pass** if an `Order` class exists with private fields (Java) or dataclass/attributes (Python), constructor, and a `total()` method used in computation.                                                   |
| Write & execute unit tests                   | Test runner               | **Pass** if at least **2** tests are present and pass (Python `unittest`, Java `JUnit`).                                                                                                                    |

### Suggested Auto‑Grader Steps (pseudo):

1. **Build/Run**:

   * Python: `python process_orders.py --input orders.csv --threshold 100`
   * Java: `javac *.java && java OrderProcessor --input orders.csv --threshold 100`
2. **Check outputs**:

   * `summary.json` parses; keys present; numbers within tolerance
   * `high_value_orders.csv` exists and header matches input
3. **Static checks**: scan for `class Order`, `def total`/`public BigDecimal total()`; presence of `for`/`if`
4. **Exception check**: run with bad path; expect non‑zero exit
5. **Run tests**:

   * Python: `python -m unittest -q`
   * Java: run JUnit; expect 2+ tests and all pass

### Tolerances & Edge Rules

* Floating‑point rounded to 2 decimals in outputs.
* Tie for top category by revenue broken alphabetically.
* Empty/invalid file → error exit; mixture of valid/invalid rows → process valid ones only.

---

## What to Submit

* Your source files (Python or Java).
* Your test files.
* The generated `summary.json` and `high_value_orders.csv` from running on the provided sample or grader’s dataset.
* (Optional) `run.log` if you implemented logging.
