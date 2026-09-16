import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text

##Conexao com o banco
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)

db_user = os.getenv("POSTGRES_USER")
db_password = os.getenv("POSTGRES_PASSWORD")
db_name = os.getenv("POSTGRES_DB")
db_port = os.getenv("POSTGRES_PORT")

db_config = {
    "POSTGRES_USER": db_user,
    "POSTGRES_PASSWORD": db_password,
    "POSTGRES_DB": db_name,
    "POSTGRES_PORT": db_port
}

missing_envs_vars = [name for name, value in db_config.items() if not value]

if missing_envs_vars:
    raise ValueError(f"Variveis de ambiente ausentes: {missing_envs_vars}")

database_url = URL.create(
    drivername="postgresql+psycopg",
    username=db_user,
    password=db_password,
    host="localhost",
    port=int(db_port),
    database=db_name,
)

engine = create_engine(database_url)

##Funcoes
def reset_table(engine):
    statement = text("TRUNCATE TABLE order_items, products, customers RESTART IDENTITY")

    with engine.begin() as connection:
        connection.execute(statement)

def reformat_date(df, column):
        df[column] = pd.to_datetime(
        df[column],
        format="%Y-%m-%d",
        errors="raise"
    ).dt.date

def reformat_numeric(df, column):
        df[column] = pd.to_numeric(
        df[column],
        errors="raise"
    )

##Load dos dados para o banco
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

df_customers = pd.read_csv(RAW_DATA_DIR / "customers.csv")
df_products = pd.read_csv(RAW_DATA_DIR / "products.csv")
df_orders = pd.read_csv(RAW_DATA_DIR / "orders.csv")

reformat_date(df_customers, "signup_date")
reformat_date(df_orders, "order_date")

reformat_numeric(df_orders, "quantity")
reformat_numeric(df_orders, "unit_price")

reset_table(engine)

customer_rows_loaded = df_customers.to_sql(
                name="customers",
                con=engine,
                if_exists="append",
                index=False,
                method="multi",
                )

products_rows_loaded = df_products.to_sql(
                name="products",
                con=engine,
                if_exists="append",
                index=False,
                method="multi"
)

orders_rows_loaded = df_orders.to_sql(
                name="order_items",
                con=engine,
                if_exists="append",
                index=False,
                method="multi"
)

with engine.connect() as connection:
    result = connection.execute(text("SELECT COUNT(*) FROM customers"))
    print(f"quantidade de clientes no banco: {result.scalar_one()}")

with engine.connect() as connection:
    result = connection.execute(text("SELECT COUNT(*) FROM products"))
    print(f"quantidade de produtos no banco: {result.scalar_one()}")

with engine.connect() as connection:
    result = connection.execute(text("SELECT COUNT(*) FROM order_items"))
    print(f"quantidade de pedidos no banco: {result.scalar_one()}")

print(f"Linhas lidas no CSV 'customers.csv': {len(df_customers)}")
print(f"Linhas lidas no CSV 'products.csv': {len(df_products)}")
print(f"Linhas lidas no CSV 'orders.csv': {len(df_orders)}")