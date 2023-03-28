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

class Neo4jIngestion:

    def __init__(self, graph):
        self.graph = graph

    def create_node(self, label, properties):
        node = Node(label, **properties)
        self.graph.create(node)
        return node

    def create_relationship(self, start_node, relationship_type, end_node, properties=None):
        rel = Relationship(start_node, relationship_type, end_node, **(properties or {}))
        self.graph.create(rel)
        return rel

class App:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

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

def parse_xml(local_xml_path, **kwargs):
    schema = xmlschema.XMLSchema('https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot.xsd')
    with open(local_xml_path, "r", encoding="utf-8") as f:
        xml_content = f.read()

    entry_dict = schema.to_dict(xml_content)
    ti = kwargs['ti']
    ti.xcom_push(key='data', value=entry_dict)
    return entry_dict
 
def store_data_in_neo4j(uri, user, password, graph, **kwargs):
    graph = Graph(uri, auth=(user, password))
    driver = GraphDatabase.driver(uri, auth=basic_auth(user, password))
    ti = kwargs['ti']
    # Serialize driver as string to avoid "Object of type BoltDriver is not JSON serializable"
    serialized_driver = f"{driver.address.host}:{driver.address.port}"
    ti.xcom_push(key='neo4j_driver', value=serialized_driver)
    
    data = ti.xcom_pull(task_ids='parse_uniprot_xml', key='data')

    entry_list = data.get("entry", [])

    if not entry_list or not isinstance(entry_list, list) or len(entry_list) == 0:
        logging.error("Entry list is empty or not a list")
        return

    

def parse_protein(entry):
    protein = entry.find("protein")
    if protein is not None:
        accession = entry.find("accession").text
        recommended_name = protein.find("recommendedName")
        if recommended_name is not None:
            full_name = recommended_name.find("fullName").text
            return {"accession": accession, "recommendedName": {"fullName": full_name}}
    return None


def parse_gene(entry):
    gene = entry.find("gene")
    if gene is not None:
        name = gene.findall("name")
        if name:
            return {"name": [n.text for n in name]}
    return None


def parse_organism(entry):
    organism = entry.find("organism")
    if organism is not None:
        name = organism.findall("name")
        db_reference = organism.find("dbReference")
        if name and db_reference is not None:
            return {"name": [n.text for n in name], "dbReference": {"id": db_reference.get("id")}}
    return None

def create_node_and_relationship(graph, entry):
    protein = parse_protein(entry)
    gene = parse_gene(entry)
    organism = parse_organism(entry)

    if protein and gene and organism:
        # Create Protein, Gene, and Organism nodes
        protein_node = Node("Protein", id=protein["accession"])
        gene_node = Node("Gene", name=gene["name"][0])
        organism_node = Node("Organism", name=organism["name"][0], taxonomy_id=organism["dbReference"]["id"])
        graph.merge(protein_node, "Protein", "id")
        graph.merge(gene_node, "Gene", "name")
        graph.merge(organism_node, "Organism", "name", "taxonomy_id")

        # Create FullName node and HAS_FULL_NAME relationship
        full_name_node = Node("FullName", name=protein["recommendedName"]["fullName"])
        graph.merge(full_name_node, "FullName", "name")
        full_name_rel = Relationship(protein_node, "HAS_FULL_NAME", full_name_node)
        graph.create(full_name_rel)

        # Create CODES_FOR and BELONGS_TO relationships
        codes_for_rel = Relationship(protein_node, "CODES_FOR", gene_node)
        graph.create(codes_for_rel)
        belongs_to_rel = Relationship(gene_node, "BELONGS_TO", organism_node)
        graph.create(belongs_to_rel)
