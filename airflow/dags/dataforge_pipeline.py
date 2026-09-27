from datetime import datetime

from airflow.providers.standard.operators.bash import BashOperator  # type: ignore
from airflow.providers.standard.operators.empty import EmptyOperator  # type: ignore

from airflow import DAG

with DAG(
    dag_id="dataforge_pipeline",
    description="Orquestra a pipeline de dados do projeto DataForge Commerce",
    start_date=datetime(2025,1,1),  # noqa: DTZ001
    schedule=None,
    catchup=False,
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

    end_pipeline = EmptyOperator(
        task_id="end_pipeline",
    )

    start_pipeline >> generate_raw_data >> validate_raw_data >> load_raw_data >> validate_loaded_data >> end_pipeline