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

#########Formata as datas do CSV
def validate_date_format(df, column_name, date_format, table_name):
    parsed_dates = pd.to_datetime(df[column_name], format=date_format, errors="coerce")

    invalid_date_mask = parsed_dates.isna()
    invalid_date_rows = df[invalid_date_mask]

    if not invalid_date_rows.empty:
        raise ValueError(f"Data invalida na tabela {table_name}, coluna {column_name}:{invalid_date_rows.to_dict(orient='records')}")

##########Valida os precos da coluna
def validate_positive_numeric(df, column_name, table_name):
    numeric_values = pd.to_numeric(df[column_name], errors="coerce")

    invalid_numeric_mask = numeric_values.isna() | (numeric_values <= 0)
    invalid_numeric_rows = df[invalid_numeric_mask]

    if not invalid_numeric_rows.empty:
        raise ValueError(f"Valor numerico invalido na tabela {table_name}, coluna {column_name}: {invalid_numeric_rows.to_dict(orient='records')}")

##########Valida os numeros referentes a quantidade nas colunas
def validate_positive_integer(df, column_name, table_name):
    numeric_values  = pd.to_numeric(df[column_name], errors="coerce")

    invalid_integer_mask = numeric_values .isna() | (numeric_values  <= 0) | (numeric_values % 1 != 0)
    invalid_integer_rows = df[invalid_integer_mask]

    if not invalid_integer_rows.empty:
        raise ValueError(f"Existem valores não positivos, não inteiros ou inválidos na tabela {table_name}, coluna {column_name}: {invalid_integer_rows.to_dict(orient="records")}")

##########Valida as FKs
def validate_foreign_key(df, column_name, reference_df, reference_column, table_name, reference_table_name):
    invalid_fk_mask = ~df[column_name].isin(reference_df[reference_column])
    invalid_fk_rows = df[invalid_fk_mask]

    if not invalid_fk_rows.empty:
        raise ValueError(f"As foreignKeys da tabela {table_name}, coluna {column_name} náo foram encontradas na tabela {reference_table_name}, coluna {reference_column}: {invalid_fk_rows.to_dict(orient="records")}")

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
    validate_date_format(customers_df, "signup_date", "%Y-%m-%d", "Customers")

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
    validate_positive_numeric(products_df, "unit_price", "Products")

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
    validate_foreign_key(orders_df, "product_id", products_df, "product_id", "Orders", "Products")

    ###########Valida se o id do customer existe no csv dos customers
    validate_foreign_key(orders_df, "customer_id", customers_df, "customer_id", "Orders", "Customer")

    #############Valida formato da Data
    validate_date_format(orders_df, "order_date", "%Y-%m-%d", "Orders")

    ######## valida valores zerado e nao numericos na coluna quantity do orders
    validate_positive_integer(orders_df, "quantity", "Orders")

    ######## validacao de valor do produto eh maior que 0
    validate_positive_numeric(orders_df, "unit_price", "Orders")

    ######## Valida status
    order_status = ["completed", "cancelled", "refunded"]

    order_invalid_status = orders_df[~orders_df["status"].isin(order_status)]

    if not order_invalid_status.empty:
        invalid_status = order_invalid_status["status"].unique().tolist()
        raise ValueError(f"Status invalido: {invalid_status}")

    print("A validacao dos pedidos ocorreu com sucesso!")

if __name__ == "__main__":
    main()