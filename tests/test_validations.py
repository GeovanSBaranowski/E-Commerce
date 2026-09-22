import pandas as pd
import pytest

from src.validate_raw_data import (validate_no_nulls, validate_required_columns, validate_unique_values)

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