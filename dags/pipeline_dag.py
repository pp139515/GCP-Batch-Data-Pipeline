from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import subprocess

def run_script(script_path):
    result = subprocess.run(
        ["python", script_path],
        check=True,
        capture_output=True,
        text=True,
        cwd="/opt/airflow"
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

with DAG(
    dag_id="gcp_batch_pipeline",
    start_date=datetime(2026, 6, 1),
    schedule_interval="@daily",
    catchup=False,
) as dag:

    extract = PythonOperator(
        task_id="extract",
        python_callable=run_script,
        op_args=["/opt/airflow/scripts/extract.py"],
    )

    transform = PythonOperator(
        task_id="transform",
        python_callable=run_script,
        op_args=["/opt/airflow/scripts/transform.py"],
    )

    load = PythonOperator(
        task_id="load",
        python_callable=run_script,
        op_args=["/opt/airflow/scripts/load.py"],
    )

    extract >> transform >> load