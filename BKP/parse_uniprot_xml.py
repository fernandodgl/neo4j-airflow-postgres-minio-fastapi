import os
import xml.etree.ElementTree as ET
import requests
from minio import Minio
from minio.error import S3Error
from neo4j import GraphDatabase, basic_auth

def download_xml_from_minio(bucket_name, object_name, minio_client, local_xml_path):
    try:
        os.makedirs(os.path.dirname(local_xml_path), exist_ok=True)
        data = minio_client.get_object(bucket_name, object_name)
        with open(local_xml_path, 'wb') as file:
            for d in data.stream(32 * 1024):
                file.write(d)
    except S3Error as err:
        print(f"Error: {err}")

def parse_uniprot_xml(file_name):
    try:
        tree = ET.parse(file_name, parser=ET.XMLParser(encoding='utf-8'))
        root = tree.getroot()
        # Parse the XML data and return it as a dictionary or other data structure
    except ET.ParseError as e:
        # Log the error message and continue execution
        print(f"Error parsing XML file: {e}... continuing...")
        return {}
    tree = ET.parse(file_name, parser=ET.XMLParser(encoding='utf-8'))
    root = tree.getroot()
    parsed_data = []
    
    for child in root:
        protein_id = None
        protein_name = None
        gene_id = None
        gene_name = None
        organism_id = None
        organism_name = None
        
        if child.tag == '{http://uniprot.org/uniprot}entry':
            for entry_child in child:
                if entry_child.tag == '{http://uniprot.org/uniprot}accession':
                    protein_id = entry_child.text
                elif entry_child.tag == '{http://uniprot.org/uniprot}protein':
                    for protein_child in entry_child:
                        if protein_child.tag == '{http://uniprot.org/uniprot}recommendedName':
                            for recommended_name_child in protein_child:
                                if recommended_name_child.tag == '{http://uniprot.org/uniprot}fullName':
                                    protein_name = recommended_name_child.text
                        elif protein_child.tag == '{http://uniprot.org/uniprot}alternativeName':
                            for alternative_name_child in protein_child:
                                if alternative_name_child.tag == '{http://uniprot.org/uniprot}fullName':
                                    protein_name = alternative_name_child.text
                elif entry_child.tag == '{http://uniprot.org/uniprot}gene':
                    gene_id = entry_child.get('id')
                    for gene_child in entry_child:
                        if gene_child.tag == '{http://uniprot.org/uniprot}name':
                            gene_name = gene_child.text
                elif entry_child.tag == '{http://uniprot.org/uniprot}organism':
                    organism_id = entry_child.find('{http://uniprot.org/uniprot}dbReference').get('id')
                    organism_name = entry_child.find('{http://uniprot.org/uniprot}name').text
        
        parsed_data.append({
            'protein_id': protein_id,
            'protein_name': protein_name,
            'gene_id': gene_id,
            'gene_name': gene_name,
            'organism_id': organism_id,
            'organism_name': organism_name
        })
    
    return parsed_data

def connect_to_neo4j(uri, user, password):
    driver = GraphDatabase.driver(uri, auth=basic_auth(user, password))
    return driver

def store_data_in_neo4j(driver, parsed_data):
    protein_label = "Protein"
    gene_label = "Gene"
    organism_label = "Organism"
    codes_for_rel = "CODES_FOR"
    organism_rel = "BELONGS_TO"

    with driver.session() as session:
        for data in parsed_data:
            protein_id = data['protein_id']
            protein_name = data['protein_name']
            gene_id = data['gene_id']
            gene_name = data['gene_name']
            organism_id = data['organism_id']
            organism_name = data['organism_name']

            # Create or update Protein node
            session.run(
                f"MERGE ({protein_label}:{protein_label} {{id: $id}}) "
                f"SET {protein_label}.name = $name",
                id=protein_id,
                name=protein_name
            )

            # Create or update Gene node and CODES_FOR relationship
            if gene_id is not None and gene_name is not None:
                session.run(
                    f"MERGE ({gene_label}:{gene_label} {{id: $id}}) "
                    f"SET {gene_label}.name = $name",
                    id=gene_id,
                    name=gene_name
                )
                session.run(
                    f"MATCH (p:{protein_label} {{id: $protein_id}}), (g:{gene_label} {{id: $gene_id}}) "
                    f"MERGE (p)-[:{codes_for_rel}]->(g)",
                    protein_id=protein_id,
                    gene_id=gene_id
                )

            # Create or update Organism node and BELONGS_TO relationship
            session.run(
                f"MERGE ({organism_label}:{organism_label} {{id: $id}}) "
                f"SET {organism_label}.name = $name",
                id=organism_id,
                name=organism_name
            )
            session.run(
                f"MATCH (p:{protein_label} {{id: $protein_id}}), (o:{organism_label} {{id: $organism_id}}) "
                f"MERGE (p)-[:{organism_rel}]->(o)",
                protein_id=protein_id,
                organism_id=organism_id
            )