import os
import xmlschema
from minio import Minio
from minio.error import S3Error
from neo4j import GraphDatabase
from lxml import etree
from airflow.models import TaskInstance
import logging
from neo4j import GraphDatabase

class App:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    @staticmethod
    def _create_and_return_node_and_relationship(tx, entry):
        protein = parse_protein(entry)
        gene = parse_gene(entry)
        #organism = parse_organism(entry)

        if protein and gene: # and organism:
            query = (
                "MERGE (protein_node:Protein {id: $protein_accession}) "
                "MERGE (gene_node:Gene {name: $gene_name}) "
                #"MERGE (organism_node:Organism {name: $organism_name, taxonomy_id: $organism_taxonomy_id}) "
                "MERGE (full_name_node:FullName {name: $protein_full_name}) "
                "MERGE (protein_node)-[:HAS_FULL_NAME]->(full_name_node) "
                "MERGE (protein_node)-[:CODES_FOR]->(gene_node) "
                #"MERGE (gene_node)-[:BELONGS_TO]->(organism_node)"
            )

            tx.run(query, protein_accession=protein["accession"], protein_full_name=protein["recommendedName"]["fullName"],
                   gene_name=gene["name"][0]) #, organism_name=organism["name"][0], organism_taxonomy_id=organism["dbReference"]["id"])

    def create_node_and_relationship(self, entry):
        with self.driver.session() as session:
            session.write_transaction(self._create_and_return_node_and_relationship, entry)


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
 
def store_data_in_neo4j(**kwargs):
    uri = "bolt://neo4j:7687"
    user = "neo4j"
    password = "password"

    app = App(uri, user, password)
    ti = kwargs['ti']
    data = ti.xcom_pull(task_ids='parse_uniprot_xml', key='data')

    entry_list = data.get("entry", [])

    if not entry_list or not isinstance(entry_list, list) or len(entry_list) == 0:
        logging.error("Entry list is empty or not a list")
        return

    for entry in entry_list:
        app.create_node_and_relationship(entry)

    app.close()
    
def parse_protein(entry):
    protein = entry.get("protein")
    if protein is not None:
        recommended_name = protein.get("recommendedName")
        if recommended_name:
            return {
                "accession": entry["accession"],
                "recommendedName": {
                    "fullName": recommended_name["fullName"],
                    "shortName": recommended_name.get("shortName")
                }
            }
    return None

def parse_gene(entry):
    gene_list = entry.get("gene")
    if gene_list:
        for gene in gene_list:
            name = gene.get("name")
            if name:
                return {"name": name[0].get("$")}
    return None

# def parse_organism(entry):
#     organism = entry.get("organism")
#     if organism is not None:
#         name = organism.get("name")
#         db_reference = organism.get("dbReference")
#         if name and db_reference is not None:
#             return {"name": name, "dbReference": {"id": db_reference[0].get("id")}}
#     return None

