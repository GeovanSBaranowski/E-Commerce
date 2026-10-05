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
    tags=["dataforge", "ecommerce"]
) as dag:
    start_pipeline = EmptyOperator(
        task_id="start_pipeline",
    )

    check_database = SQLExecuteQueryOperator(
        task_id="check_database",
        conn_id="dataforge_postgres",
        sql="SELECT 1",
        retries=5,
        retry_delay=timedelta(minutes=1)
    )

    process_incoming_batches = BashOperator(
        task_id="process_incoming_batches",
        bash_command="cd /opt/dataforge && python src/run_incremental_pipeline.py",
        env={"POSTGRES_HOST": "host.docker.internal"},
        append_env=True,
        retries=2,
        retry_delay=timedelta(minutes=1)
    )

    create_analytics_layer = SQLExecuteQueryOperator(
        task_id="create_analytics_layer",
        conn_id="dataforge_postgres",
        sql=ANALYTICS_SQL,
        retries=2,
        retry_delay=timedelta(minutes=1),
        retry_exponential_backoff=True,
    )

    end_pipeline = EmptyOperator(
        task_id="end_pipeline",
    )

    start_pipeline >> check_database >> process_incoming_batches >> create_analytics_layer >> end_pipeline