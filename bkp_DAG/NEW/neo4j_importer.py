import requests
from py2neo import Graph, Node, Relationship
import xml.etree.ElementTree as ET

NEO4J_URI = "bolt://neo4j:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"
UNIPROT_URL = "https://www.uniprot.org/uniprot/?query=*&fil=organism%3A%22Homo+sapiens+%28Human%29+%5B9606%5D%22&format=xml"

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




# def import_uniprot_data():
#     graph = Graph(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

#     # Download UniProt data
#     response = requests.get(UNIPROT_URL)
#     xml_data = response.text

#     # Here you can add code to import the XML data into Neo4j without parsing.

#     return "Data imported successfully"
