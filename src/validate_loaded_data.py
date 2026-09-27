from pathlib import Path

import pandas as pd
from sqlalchemy import text

from database import get_engine

RAW_DATA_DIR = Path("data/raw")

def validate_row_count(engine, table_name, expected_count):
    statement = text(f"SELECT COUNT(*) FROM {table_name}")

    with engine.connect() as connection:
        database_count = connection.execute(statement).scalar_one()

    if database_count != expected_count:
        raise ValueError(
            f"Quantidade de linhas divergentes na tabela {table_name}: "
            f"Esperado {expected_count}, encontrado {database_count}"
        )

    print(
        f"Quantidade validada na tabela {table_name}: "
        f"{database_count} linhas"
    )

def main():
    engine = get_engine()

    source_files = {
        "customers": "customers.csv",
        "products": "products.csv",
        "order_items": "orders.csv"
    }
    
    for table_name, file_name in source_files.items():
        csv_path = RAW_DATA_DIR / file_name
        expected_count = len(pd.read_csv(csv_path))
        validate_row_count(engine, table_name, expected_count)

if __name__ == "__main__":
    main()

