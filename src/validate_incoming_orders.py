from pathlib import Path

import pandas as pd

from validate_raw_data import validate_orders

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
INCOMING_DATA_DIR = PROJECT_ROOT / "data" / "incoming"

def validate_incoming_orders(csv_path):
    orders_df = pd.read_csv(csv_path)
    customers_df = pd.read_csv(RAW_DATA_DIR / "customers.csv")
    products_df = pd.read_csv(RAW_DATA_DIR / "products.csv")

    validate_orders(orders_df, customers_df, products_df)
    print("Pedidos incrementais validados com sucesso")

    return orders_df

if __name__ == "__main__":
    validate_incoming_orders(INCOMING_DATA_DIR / "orders_2026-10-01.csv")