FROM apache/airflow:3.0.6-python3.12
RUN pip install --no-cache-dir dbt-duckdb==1.9.4 duckdb==1.3.2
