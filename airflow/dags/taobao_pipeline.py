from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator


with DAG(
    dag_id="taobao_daily_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="0 2 * * *",
    catchup=False,
    max_active_runs=1,
    tags=["portfolio", "data-engineering"],
) as dag:
    load = BashOperator(
        task_id="load_raw_orders",
        bash_command="python /opt/airflow/project/scripts/load_orders.py --input /opt/airflow/project/data/orders.csv --database /opt/airflow/data/warehouse.duckdb",
    )
    build_and_test = BashOperator(
        task_id="dbt_build",
        env={"TAOBAO_DUCKDB_PATH": "/opt/airflow/data/warehouse.duckdb"},
        append_env=True,
        bash_command="cd /opt/airflow/project && dbt build --profiles-dir .",
    )
    load >> build_and_test
