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
