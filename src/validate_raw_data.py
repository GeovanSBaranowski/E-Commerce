from pathlib import Path

import pandas as pd

RAW_DATA_DIR = Path("data/raw")
customers_df = pd.read_csv(RAW_DATA_DIR / "customers.csv")

customer_expected_coluns = ["customer_id","name","email","signup_date","city","state"]
customer_missing_colums = set(customer_expected_coluns) - set(customers_df.columns)

if customer_missing_colums:
    raise ValueError(f"Colunas ausentes: {customer_missing_colums}")
else:
    print("Todas as colunas estao presentes")

customer_null_columns = customers_df.isna().sum()
customer_null_columns_true = customer_null_columns[customer_null_columns > 0]

if not customer_null_columns_true.empty:
    raise ValueError(f"Colunas com valores nulos: {customer_null_columns_true.to_dict()}")

customer_duplicate_ids = customers_df[customers_df["customer_id"].duplicated(keep=False)].sort_values("customer_id")
duplicate_email = customers_df[customers_df["email"].duplicated(keep=False)].sort_values("email")

if not customer_duplicate_ids.empty:
    raise ValueError(f"Clientes com customer_id duplicado: {customer_duplicate_ids.to_dict(orient='records')}")

if not duplicate_email.empty:
    raise ValueError(f"Clientes com email duplicado: {duplicate_email.to_dict(orient='records')}")

customers_sign_up = pd.to_datetime(customers_df["signup_date"], format="%Y-%m-%d", errors="coerce")

invalid_sign_up_date_mask = customers_sign_up.isna()
invalid_sign_up_date_rows = customers_df[invalid_sign_up_date_mask]

if not invalid_sign_up_date_rows.empty:
    raise ValueError(f"Data de inscricao invalida:{invalid_sign_up_date_rows.to_dict(orient='records')}")

print("A validacao dos clientes ocorreu com sucesso!")

########## produto ###########

## dataframe do produto
products_df = pd.read_csv(RAW_DATA_DIR / "products.csv")
coluns_products = ["product_id","product_name","category","unit_price"]

## validacao de colunas ausentes
product_missing_colums = set(coluns_products) - set(products_df.columns)

if product_missing_colums:
    raise ValueError(f"A colunas dos produtos estao incompletas: {product_missing_colums}")
else:
    print("Todas as colunas estao presentes")

product_null_columns = products_df.isna().sum()
product_null_columns_true = product_null_columns[product_null_columns > 0]

if not product_null_columns_true.empty:
    raise ValueError(f"Os seguintes valores estao nulos: {product_null_columns_true.to_dict()}")

##validacao de IDs duplicados
product_duplicate_ids = products_df[products_df["product_id"].duplicated(keep=False)].sort_values("product_id")

if not product_duplicate_ids.empty:
    raise ValueError(f"Produto com id duplicado: {product_duplicate_ids.to_dict(orient='records')}")

## validacao do preco do produto
unit_price = pd.to_numeric(products_df["unit_price"], errors="coerce")

invalid_price_mask = unit_price.isna()
invalid_price_records = products_df[invalid_price_mask]

if not invalid_price_records.empty:
    raise ValueError(f"Preco do produto invalido: {invalid_price_records.to_dict(orient='records')}")

## validacao de valor do produto eh maior que 0
non_positive_price_rows = products_df[unit_price <= 0]

if not non_positive_price_rows.empty:
    raise ValueError(f"Existem produtos com valores negativos ou iguais a 0: {non_positive_price_rows.to_string(index=False)}")

##validacao das categorias
categories = ["Eletronicos", "Livros", "Casa", "Esporte"]

invalid_category_rows = products_df[~products_df["category"].isin(categories)]

if not invalid_category_rows.empty:
    invalid_categories = invalid_category_rows["category"].unique().tolist()
    raise ValueError(f"Existem categorias invalidas: {invalid_categories}")

print("A validacao dos produtos ocorreu com sucesso!")

############# orders

orders_df = pd.read_csv(RAW_DATA_DIR / "orders.csv")

############# valida colunas do csv
orders_expected_coluns = ["order_id","customer_id","product_id","order_date","quantity","unit_price","status"]
orders_missing_colums = set(orders_expected_coluns) - set(orders_df.columns)

if orders_missing_colums:
    raise ValueError(f"Colunas ausentes: {orders_missing_colums}")
else:
    print("Todas as colunas estao presentes")

############valida valores nulos nas colunas
orders_null_columns = orders_df.isna().sum()
orders_null_columns_true =orders_null_columns[orders_null_columns > 0]

if not orders_null_columns_true.empty:
    raise ValueError(f"Colunas com valores nulos: {orders_null_columns_true.to_dict()}")

###########Valida se o id do produto existe no csv dos products
invalid_product_id_mask = ~orders_df["product_id"].isin(products_df["product_id"])
invalid_product_id_rows = orders_df[invalid_product_id_mask]

if not invalid_product_id_rows.empty:
    raise ValueError(f"Linhas com customer_id invalidos: {invalid_product_id_rows.to_dict()}")

###########Valida se o id do customer existe no csv dos customers
invalid_customer_id_mask = ~orders_df["customer_id"].isin(customers_df["customer_id"])
invalid_customer_id_rows = orders_df[invalid_customer_id_mask]

if not invalid_customer_id_rows.empty:
    raise ValueError(f"Linhas com customer_id invalidos: {invalid_customer_id_rows.to_dict()}")

#############Valida formato da Data
order_date = pd.to_datetime(orders_df["order_date"], format="%Y-%m-%d", errors="coerce")

invalid_order_date_mask = order_date.isna()
invalid_date_rows = orders_df[invalid_order_date_mask]

if not invalid_date_rows.empty:
    raise ValueError(f"Data do pedido invalida:{invalid_date_rows.to_dict(orient='records')}")

######## valida valores zerado e nao numericos
order_quantity = pd.to_numeric(orders_df["quantity"], errors="coerce")

invalid_quantity_mask = order_quantity.isna() | (order_quantity <= 0)
invalid_quantity_rows = orders_df[invalid_quantity_mask]

if not invalid_quantity_rows.empty:
    raise ValueError(f"existem ordens com quantidade de produto igual a 0 ou com valores nao numericos: {invalid_quantity_rows.to_dict(orient="records")}")

######## validacao de valor do produto eh maior que 0
order_unit_price = pd.to_numeric(orders_df["unit_price"], errors="coerce")

invalid_unit_price_mask = order_unit_price.isna() | (order_unit_price <= 0)
invalid_unit_price_rows = orders_df[invalid_unit_price_mask]

if not invalid_unit_price_rows.empty:
    raise ValueError(f"Existem produtos com valores negativos ou iguais a 0: {invalid_unit_price_rows.to_string(index=False)}")

######## Valida status
order_status = ["completed", "cancelled", "refunded"]

order_invalid_status = orders_df[~orders_df["status"].isin(order_status)]

if not order_invalid_status.empty:
    invalid_status = order_invalid_status["status"].unique().tolist()
    raise ValueError(f"Status invalido: {invalid_status}")

print("A validacao dos pedidos ocorreu com sucesso!")