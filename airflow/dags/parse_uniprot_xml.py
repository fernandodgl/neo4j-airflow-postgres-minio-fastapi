import os
import re
import xmlschema
from minio import Minio
from minio.error import S3Error
from neo4j import GraphDatabase, basic_auth
from py2neo import Graph, Node, Relationship
import xml.etree.ElementTree as ET 
from lxml import etree
from airflow.models import TaskInstance
import logging


def download_xml_from_minio(bucket_name, object_name, minio_client, local_xml_path):
    try:
        os.makedirs(os.path.dirname(local_xml_path), exist_ok=True)
        data = minio_client.get_object(bucket_name, object_name)
        with open(local_xml_path, 'wb') as file:
            for d in data.stream(32 * 1024):
                file.write(d)
        # Check if the file has been successfully downloaded and is not empty
        if os.path.exists(local_xml_path) and os.path.getsize(local_xml_path) > 0:
            print(f"File {local_xml_path} successfully downloaded.")
            with open(local_xml_path, 'r') as file:
                print("File content preview:")
                print(file.read(100))  # Print the first 100 characters of the file
        else:
            print(f"File {local_xml_path} is empty or not found.")
    except S3Error as err:
        print(f"Error: {err}")

def parse_uniprot_xml(local_xml_path, **kwargs):
    schema = xmlschema.XMLSchema('https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot.xsd')
    with open(local_xml_path, "r", encoding="utf-8") as f:
        xml_content = f.read()

    entry_dict = schema.to_dict(xml_content)
    ti = kwargs['ti']
    ti.xcom_push(key='data', value=entry_dict)
    return entry_dict
    
def connect_to_neo4j(uri, user, password, **kwargs):
    driver = GraphDatabase.driver(uri, auth=basic_auth(user, password))
    ti = kwargs['ti']
    # Serialize driver as string to avoid "Object of type BoltDriver is not JSON serializable"
    serialized_driver = f"{driver.address.host}:{driver.address.port}"
    ti.xcom_push(key='neo4j_driver', value=serialized_driver)
    return 'Connection successful'

def store_data_in_neo4j(graph, **kwargs):
    ti = kwargs['ti']
    data = ti.xcom_pull(task_ids='parse_uniprot_xml', key='data')

    entry_list = data.get("entry", [])

    if not entry_list or not isinstance(entry_list, list) or len(entry_list) == 0:
        logging.error("Entry list is empty or not a list")
        return

    entry = entry_list[0]

    protein = entry.get("entry", {}).get("protein")
    gene = entry.get("entry", {}).get("gene")
    organism = entry.get("entry", {}).get("organism")

    if protein and gene and organism:
        protein_node = Node("Protein", name=protein["recommendedName"]["fullName"])
        gene_node = Node("Gene", name=gene["name"][0])
        organism_node = Node("Organism", name=organism["name"][0])

        graph.create(protein_node)
        graph.create(gene_node)
        graph.create(organism_node)

        graph.create(Relationship(protein_node, "CODES_FOR", gene_node))
        graph.create(Relationship(gene_node, "BELONGS_TO", organism_node))


