import sys
sys.path.append('/path/to/your/minio/directory')
from datetime import datetime, timedelta
from parse_uniprot_xml import download_xml_from_minio, parse_uniprot_xml, connect_to_neo4j, store_data_in_neo4j
from airflow import DAG
from airflow.operators.python import PythonOperator
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
}

dag = DAG(
    'uniprot_data_pipeline',
    default_args=default_args,
    description='UniProt XML Data Pipeline',
    schedule_interval=timedelta(days=1),
    catchup=False,
    max_active_runs=1
)

def execute_pipeline():
    # Download the XML file from MinIO
    minio_client = Minio(
        "minio:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )
    bucket_name = "bucket"
    object_name = "Q9Y261.xml"
    download_xml_from_minio(bucket_name, object_name, minio_client)

    # Parse the XML file and process the data
    parsed_data = parse_uniprot_xml(object_name)

    # Connect to the Neo4j database
    uri = "bolt://neo4j:7687"
    user = "neo4j"
    password = "password"
    driver = connect_to_neo4j(uri, user, password)

    # Store the parsed data in the Neo4j database
    store_data_in_neo4j(driver, parsed_data)

    # Close the Neo4j driver
    driver.close()

execute_pipeline_task = PythonOperator(
    task_id="execute_pipeline",
    python_callable=execute_pipeline,
    dag=dag,
)
