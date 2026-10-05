import argparse
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from database import get_engine
from validate_incoming_orders import validate_incoming_orders

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INCOMING_FILE = PROJECT_ROOT / "data" / "incoming" / "orders_2026-10-01.csv"

def main(csv_path):
    orders_df = validate_incoming_orders(csv_path)
    print(f"Linhas recebidas: {len(orders_df)}")

    engine = get_engine()

    with engine.connect() as connection:
        total = connection.execute(
            text("SELECT COUNT(*) FROM order_items")
        ).scalar_one()

    print(f"Itens existentes no banco: {total}")

    orders_df["order_date"] = pd.to_datetime(
        orders_df["order_date"], format="%Y-%m-%d"
    ).dt.date

    insert_order = text("""
        INSERT INTO order_items
            (order_id, item_number, customer_id, product_id, order_date, quantity, unit_price, status)
        VALUES
            (:order_id, :item_number, :customer_id, :product_id, :order_date, :quantity, :unit_price, :status)
        ON CONFLICT
            (order_id, item_number) DO NOTHING
    """)

    with engine.begin() as connection:
        connection.execute(insert_order, orders_df.to_dict(orient="records"))
        new_total = connection.execute(
            text("SELECT COUNT(*) FROM order_items")
        ).scalar_one()

    print(f"Itens no banco apos a carga: {new_total}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", type=Path)
    args = parser.parse_args()

    main(args.csv_path)
