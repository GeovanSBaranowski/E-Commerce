from datetime import timedelta
from pathlib import Path

import pendulum  # type: ignore
from airflow.providers.common.sql.operators.sql import (  # type: ignore
    SQLExecuteQueryOperator,  # type: ignore
)
from airflow.providers.standard.operators.bash import BashOperator  # type: ignore
from airflow.providers.standard.operators.empty import EmptyOperator  # type: ignore

from airflow import DAG

ANALYTICS_SQL = Path(
    "/opt/dataforge/sql/03_create_analytics_layer.sql"
).read_text(encoding="utf-8")

with DAG(
    dag_id="dataforge_pipeline",
    description="Orquestra a pipeline de dados do projeto DataForge Commerce",
    start_date=pendulum.datetime(2025,1,1, tz="America/Sao_Paulo"),
    schedule="0 6 * * *",
    catchup=False,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=1)
    },
    tags=["dataforge", "ecommerce"]
) as dag:
    start_pipeline = EmptyOperator(
        task_id="start_pipeline",
    )

    generate_raw_data = BashOperator(
        task_id="generate_raw_data",
        bash_command="cd /opt/dataforge && python src/generate_raw_data.py"
    )

    validate_raw_data = BashOperator(
        task_id="validate_raw_data",
        bash_command="cd /opt/dataforge && python src/validate_raw_data.py"
    )

    load_raw_data = BashOperator(
        task_id="load_raw_data",
        bash_command="cd /opt/dataforge && python src/load_raw_data.py",
        env={
            "POSTGRES_HOST":"host.docker.internal",
        },
        append_env=True,
    )

    validate_loaded_data = BashOperator(
        task_id="validate_loaded_data",
        bash_command="cd /opt/dataforge && python src/validate_loaded_data.py",
        env={
            "POSTGRES_HOST": "host.docker.internal",
        },
        append_env=True,
    )

    create_analytics_layer = SQLExecuteQueryOperator(
        task_id="create_analytics_layer",
        conn_id="dataforge_postgres",
        sql=ANALYTICS_SQL,
    )

    end_pipeline = EmptyOperator(
        task_id="end_pipeline",
    )

    start_pipeline >> generate_raw_data >> validate_raw_data >> load_raw_data >> validate_loaded_data >> create_analytics_layer >> end_pipeline