from fastapi import FastAPI
from py2neo import Graph, NodeMatcher

app = FastAPI()

# Connect to the Neo4j database
graph = Graph("bolt://neo4j:7687", auth=("neo4j", "password"))

# Create a NodeMatcher instance
matcher = NodeMatcher(graph)

@app.get("/protein")
async def get_all_proteins():
    proteins = matcher.match("Protein").all()
    protein_names = [protein['name'] for protein in proteins]
    return {"proteins": protein_names}

@app.get("/gene")
async def get_all_genes():
    genes = matcher.match("Gene").all()
    gene_names = [gene['name'] for gene in genes]
    return {"genes": gene_names}

@app.get("/protein/{protein_name}")
async def get_protein(protein_name: str):
    protein = matcher.match("Protein", name=protein_name).first()
    if protein:
        return protein
    else:
        return {"error": "Protein not found"}

@app.get("/gene/{gene_name}")
async def get_gene(gene_name: str):
    gene = matcher.match("Gene", name=gene_name).first()
    if gene:
        return gene
    else:
        return {"error": "Gene not found"}

@app.get("/organism/{organism_name}")
async def get_organism(organism_name: str):
    organism = matcher.match("Organism", name=organism_name).first()
    if organism:
        return organism
    else:
        return {"error": "Organism not found"}