from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from neo4j import GraphDatabase, basic_auth
import os

app = FastAPI()

def connect_to_neo4j(uri, user, password):
    driver = GraphDatabase.driver(uri, auth=basic_auth(user, password))
    return driver

@app.get("/proteins")
def get_proteins(skip: int = 0, limit: int = 10):
    query = "MATCH (p:Protein) RETURN p.id, p.name SKIP $skip LIMIT $limit"
    result = []
    
    with driver.session() as session:
        records = session.run(query, skip=skip, limit=limit)
        for record in records:
            result.append({"id": record["p.id"], "name": record["p.name"]})
    
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Proteins not found")

@app.get("/genes")
def get_genes(skip: int = 0, limit: int = 10):
    query = "MATCH (g:Gene) RETURN g.id, g.name SKIP $skip LIMIT $limit"
    result = []
    
    with driver.session() as session:
        records = session.run(query, skip=skip, limit=limit)
        for record in records:
            result.append({"id": record["g.id"], "name": record["g.name"]})
    
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Genes not found")

@app.get("/organisms")
def get_organisms(skip: int = 0, limit: int = 10):
    query = "MATCH (o:Organism) RETURN o.id, o.name SKIP $skip LIMIT $limit"
    result = []
    
    with driver.session() as session:
        records = session.run(query, skip=skip, limit=limit)
        for record in records:
            result.append({"id": record["o.id"], "name": record["o.name"]})
    
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Organisms not found")

NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "neo4j_password")

driver = connect_to_neo4j(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
