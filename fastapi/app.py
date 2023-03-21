from fastapi import FastAPI
from py2neo import Graph, NodeMatcher

app = FastAPI()

# Connect to the Neo4j database
graph = Graph("bolt://neo4j:7687", auth=("neo4j", "password"))

# Create a NodeMatcher instance
matcher = NodeMatcher(graph)

@app.get("/protein/{protein_id}")
async def get_protein(protein_id: str):
    protein = matcher.match("Protein", id=protein_id).first()
    if protein:
        return protein
    else:
        return {"error": "Protein not found"}

@app.get("/gene/{gene_id}")
async def get_gene(gene_id: str):
    gene = matcher.match("Gene", id=gene_id).first()
    if gene:
        return gene
    else:
        return {"error": "Gene not found"}

@app.get("/organism/{organism_id}")
async def get_organism(organism_id: str):
    organism = matcher.match("Organism", id=organism_id).first()
    if organism:
        return organism
    else:
        return {"error": "Organism not found"}
