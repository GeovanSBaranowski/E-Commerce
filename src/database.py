import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine

##Conexao com o banco
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"
    

def get_engine():

    load_dotenv(ENV_FILE)
    
    db_user = os.getenv("POSTGRES_USER")
    db_password = os.getenv("POSTGRES_PASSWORD")
    db_name = os.getenv("POSTGRES_DB")
    db_port = os.getenv("POSTGRES_PORT")
    db_host = os.getenv("POSTGRES_HOST", "localhost")
    
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
        host=db_host,
        port=int(db_port),
        database=db_name,
    )
    
    db_engine = create_engine(database_url)

    return db_engine
