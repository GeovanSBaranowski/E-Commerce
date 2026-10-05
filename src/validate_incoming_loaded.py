import argparse
from pathlib import Path

import pandas as pd
from sqlalchemy import bindparam, text

from database import get_engine


def main(csv_path):
    incoming = pd.read_csv(csv_path, usecols=["order_id", "item_number"])

    if incoming.empty:
        raise ValueError("O lote esta vazio")

    order_ids = incoming["order_id"].drop_duplicates().to_list()

    statement = text("""
        SELECT
            order_id, item_number
        FROM
            order_items
        WHERE
            order_id IN :order_ids
    """).bindparams(bindparam("order_ids", expanding=True))

    with get_engine().connect() as connection:
        database_rows = connection.execute(
            statement, {"order_ids": order_ids}
        ).all()

    expected_keys = set(
        incoming[["order_id", "item_number"]].itertuples(index=False, name=None)
    )
    found_keys = {tuple(row) for row in database_rows}

    missing_keys = expected_keys - found_keys

    if missing_keys:
        raise ValueError(f"Itens do lote ausentes no banco: {sorted(missing_keys)}")

    print(f"Todos os {len(expected_keys)} itens do lote estão no banco")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", type=Path)
    args = parser.parse_args()
    main(args.csv_path)
