from pathlib import Path

import pandas as pd

RAW_DATA_DIR = Path("data/raw")

#############funcoes compartilhadas

############# valida colunas dos CSVs
def validate_required_columns(df, expected_columns, table_name):
    missing_columns = set(expected_columns) - set(df.columns)

    if missing_columns:
        raise ValueError(f"Colunas ausentes na tabela {table_name}: {missing_columns}")
    
    print(f"Todas as colunas da tabela {table_name} estao presentes")

############Valida colunas com nulos
def validate_no_nulls(df, table_name):
    null_counts = df.isna().sum()
    columns_with_nulls = null_counts[null_counts > 0]

    if not columns_with_nulls.empty:
        raise ValueError(f"Colunas com valores nulos na tabela {table_name}: {columns_with_nulls.to_dict()}")

    print(f"Todas as colunas da tabela {table_name} possuem valores")

###########Valida valores unicos
def validate_unique_values(df, column_name, table_name):
    duplicate_rows = df[df[column_name].duplicated(keep=False)].sort_values(column_name)

    if not duplicate_rows.empty:
        raise ValueError(f"Colunas com valores duplicados na tabela {table_name}, coluna {column_name}: {duplicate_rows.to_dict(orient='records')}")

    print(f"Todos os valores sao unicos na coluna {column_name} da tabela {table_name} \n")

###########main
def main():
    
    ############ leitura dos CSVs
    customers_df = pd.read_csv(RAW_DATA_DIR / "customers.csv")

    ## dataframe do produto
    products_df = pd.read_csv(RAW_DATA_DIR / "products.csv")

    ############# orders
    orders_df = pd.read_csv(RAW_DATA_DIR / "orders.csv")

    ########validacao customer

    ########valida colunas
    customer_expected_columns = ["customer_id","name","email","signup_date","city","state"]

    validate_required_columns(customers_df, customer_expected_columns, "Customer")

    ########valida nulos
    validate_no_nulls(customers_df, "Customers")

    #########valida id e email duplicado nos customers
    validate_unique_values(customers_df, "customer_id", "Customers")
    validate_unique_values(customers_df, "email", "Customers")

    ##########Valida data de inscricao
    customers_sign_up = pd.to_datetime(customers_df["signup_date"], format="%Y-%m-%d", errors="coerce")

    invalid_sign_up_date_mask = customers_sign_up.isna()
    invalid_sign_up_date_rows = customers_df[invalid_sign_up_date_mask]

    if not invalid_sign_up_date_rows.empty:
        raise ValueError(f"Data de inscricao invalida:{invalid_sign_up_date_rows.to_dict(orient='records')}")

    print("A validacao dos clientes ocorreu com sucesso!")

    ########## produto ###########

    ## validacao de colunas ausentes
    coluns_products = ["product_id","product_name","category","unit_price"]

    validate_required_columns(products_df, coluns_products, "Products")

    #######Valida colunas nulas
    validate_no_nulls(products_df, "Products")

    ##validacao de IDs duplicados
    validate_unique_values(products_df, "product_id", "Products")

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

    ############# Orders

    ############# valida colunas do csv
    orders_expected_columns = ["order_id","customer_id","product_id","order_date","quantity","unit_price","status"]

    validate_required_columns(orders_df, orders_expected_columns, "Orders")

    ############valida valores nulos nas colunas
    validate_no_nulls(orders_df, "Orders")

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

if __name__ == "__main__":
    main()