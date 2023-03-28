import sys
import os
import logging
from datetime import datetime, timedelta
from parse_uniprot_xml import download_xml_from_minio, parse_xml, store_data_in_neo4j, App 
from airflow.models import DAG, Variable
from airflow.operators.python import PythonOperator
from py2neo import Graph
from minio import Minio
from minio.error import S3Error

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 3, 19),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'max_active_runs': 4
}

dag = DAG(
    'uniprot_data_pipeline',
    default_args=default_args,
    description='uniprot_xml_datapipeline',
    schedule_interval=timedelta(days=1),
    catchup=False,
    max_active_runs=1
)

bucket_name = "bucket"
object_name = "Q9Y261.xml"
local_xml_path = os.path.join(os.path.abspath("dags"), "Q9Y261.xml")
graph = Graph("bolt://neo4j:7687", auth=("neo4j", "password"))


minio_client = Minio(
    "minio:9000",
    access_key="admin",
    secret_key="password",
    secure=False
)

uri = "bolt://neo4j:7687"
user = "neo4j"
password = "password"

download_xml_task = PythonOperator(
    task_id="download_xml",
    python_callable=download_xml_from_minio,
    op_args=[bucket_name, object_name, minio_client, local_xml_path],
    dag=dag,
)

parse_xml_task = PythonOperator(
    task_id="parse_uniprot_xml",
    python_callable=parse_xml,
    op_args=[local_xml_path],
    provide_context=True,
    dag=dag,
)

store_data_in_neo4j_task = PythonOperator(
    task_id="store_data_in_neo4j",
    python_callable=store_data_in_neo4j,
    op_kwargs={
        'app': App
    },
    provide_context=True,
    dag=dag,
)

download_xml_task >> parse_xml_task >> store_data_in_neo4j_task
