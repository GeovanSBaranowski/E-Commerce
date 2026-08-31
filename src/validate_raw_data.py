from pathlib import Path

import pandas as pd

RAW_DATA_DIR = Path("data/raw")
customers_df = pd.read_csv(RAW_DATA_DIR / "customers.csv")

expected_coluns = ["customer_id","name","email","signup_date","city","state"]

missing_colums = set(expected_coluns) - set(customers_df.columns)

if missing_colums:
    raise ValueError(f"Colunas ausentes: {missing_colums}")
else:
    print("Todas as colunas estao presentes")

nulos_por_coluna = customers_df.isna().sum()
colunas_com_nulos = nulos_por_coluna[nulos_por_coluna > 0]

if not colunas_com_nulos.empty:
    raise ValueError(f"Colunas com valores nulos: {colunas_com_nulos.to_dict()}")

duplicate_customer_ids = customers_df[customers_df["customer_id"].duplicated(keep=False)].sort_values("customer_id")
duplicate_customers_email = customers_df[customers_df["email"].duplicated(keep=False)].sort_values("email")

if not duplicate_customer_ids.empty:
    raise ValueError(f"Clientes com customer_id duplicado: {duplicate_customer_ids.to_dict(orient='records')}")

if not duplicate_customers_email.empty:
    raise ValueError(f"Clientes com email duplicado: {duplicate_customers_email.to_dict(orient='records')}")



customers_sign_up = pd.to_datetime(customers_df["signup_date"], format="%Y-%m-%d", errors="coerce")

invalid_sign_up_date_mask = customers_sign_up.isna()
invalid_sign_up_date_records = customers_df[invalid_sign_up_date_mask]

if not invalid_sign_up_date_records.empty:
    raise ValueError(f"Data de inscricao invalida:{invalid_sign_up_date_records.to_dict(orient='records')}")

print("A validacao ocorreu com sucesso!")