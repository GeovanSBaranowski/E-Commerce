import pandas as pd
import pytest

from src.validate_raw_data import (
    validate_date_format,
    validate_foreign_key,
    validate_no_nulls,
    validate_positive_integer,
    validate_positive_numeric,
    validate_required_columns,
    validate_unique_values,
)


def test_required_columns_raises_error_when_email_is_missing():

    df = pd.DataFrame({
        "customer": [1],
        "name": ["Ana"]
    })

    expected_columns = ["customer", "name", "email"]

    with pytest.raises(ValueError, match="Colunas ausentes"):
        validate_required_columns(df, expected_columns, "customer")

def test_required_columns_accepts_complete_dataframe():
    
    df = pd.DataFrame({
        "customer": [1],
        "name": ["Ana"],
        "email": ["teste@email.com"]
    })

    expected_columns = ["customer", "name", "email"]   

    validate_required_columns(df, expected_columns, "customer")

def test_columns_with_null_values_raises_error():
        
    df = pd.DataFrame({
        "customer": [1],
        "name": None,
        "email": ["teste@email.com"]
    })

    with pytest.raises(ValueError, match="Colunas com valores nulos"):
        validate_no_nulls(df, "customer")

def test_columns_with_duplicated_id_raises_error():

    df = pd.DataFrame({
        "customer_id": [1, 1],
        "name": ["Ana", "Antonio"],
        "email": ["teste@email.com", "teste2@email.com"]
    })

    with pytest.raises(ValueError, match="Colunas com valores duplicados na tabela"):
        validate_unique_values(df, "customer_id", "customer")

def test_date_format_raises_error_when_date_is_invalid():

    df = pd.DataFrame({
        "signup_date":["2025-01-01", "Teste"]
    })

    with pytest.raises(ValueError, match="Data invalida"):
        validate_date_format(df, "signup_date", "%Y-%m-%d", "Customers")

def test_positive_numeric_raises_error_when_value_is_zero():

    df = pd.DataFrame({
        "unit_price": [0]
    })

    with pytest.raises(ValueError, match="Valor numerico invalido"):
        validate_positive_numeric(df, "unit_price", "Products")

def test_positive_integer_raises_error_when_quantity_is_decimal():

    df = pd.DataFrame({
        "quantity": [0.5]
    })

    with pytest.raises(ValueError, match="Existem valores não positivos, não inteiros ou inválidos na tabela"):
        validate_positive_integer(df, "quantity", "Orders")

def test_foreign_keys_raises_error_when_product_does_not_exist():

    orders_df = pd.DataFrame({
        "product_id": [999]
    })

    products_df = pd.DataFrame({
        "product_id":[1,2]
    })

    with pytest.raises(ValueError, match="foreignKeys"):
        validate_foreign_key(orders_df, "product_id", products_df, "product_id", "Orders", "Product")
