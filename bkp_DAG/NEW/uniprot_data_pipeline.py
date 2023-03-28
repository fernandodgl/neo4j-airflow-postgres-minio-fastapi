from datetime import timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from neo4j_importer import parse_protein, parse_gene, parse_organism, create_node_and_relationship

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'uniprot_data_pipeline',
    default_args=default_args,
    description='UniProt data import pipeline',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(2),
    tags=['example'],
)

parse_protein = PythonOperator(
    task_id='parse_protein',
    python_callable=parse_protein,
    dag=dag,
)

parse_gene = PythonOperator(
    task_id='parse_gene',
    python_callable=parse_gene,
    dag=dag,
)

parse_organism = PythonOperator(
    task_id='parse_organism',
    python_callable=parse_organism,
    dag=dag,
)

create_node_relationship = PythonOperator(
    task_id='create_node_and_relations',
    python_callable=create_node_and_relationship,
    dag=dag,
)

parse_protein >> parse_gene >> parse_organism >> create_node_relationship
