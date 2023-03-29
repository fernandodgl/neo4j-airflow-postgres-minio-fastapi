
# Weave.bio Data Engineering Challenge

This project contains the following containers:

* Postgres: Postgres database for Airflow metadata 
    * Image: postgres:13
    * Database Port: 5432

* Airflow: Airflow webserver and Scheduler.
    * Image: apache/airflow:2.2.3
    * Port: 8080

* Spark: Spark Master.
    * Image: bitnami/spark:3.2.1
    * Port: 7077

* Spark-worker-N: Spark workers. More workers can be added if needed.
    * Image: bitnami/spark:3.2.1
    
* MiniO: Local Datalake
    * Image: postgres:13
    * Web console Port: 9000

* Neo4j: Postgres database for Airflow metadata 
    * Image: neo4j:4.4.0
    * Database Port: 7474

* FastAPI: Requests via API
    * Image: 0.95.0
    * Database Port: 8000

## File Structure

```bash
├── airflow
│   ├── dags
│   │   ├── parse_uniprot_xml.py
|   |   ├── uniprot_data_pipeline.py
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── requirements.txt
├── data
├── fastapi
│   │   ├── app.py
|   |   ├── Dockerfile
|   |   ├── requirements.txt
├── logs
├── minio
│   │   ├── Dockerfile
|   |   ├── requirements.txt
|   |   ├── setup.sh
└── docker-compose.yml
└── README.md
└── TODO
```

## Architecture components

![Screenshot](architecture_small.png)

## Setup

### Clone project

    $ git clone https://github.com/fernandodgl/weavebio
### Build containers

Inside the 'weavebio' folder (root)

    $ docker-compose build --no-cache

### Start containers

At the same path above:

    $ docker-compose up

If you want to run in background:

    $ docker-compose up -d

### Check if you can access:

|        Application        |URL                          |Credentials                         |
|----------------|-------------------------------|-----------------------------|
|Airflow| [http://localhost:8080](http://localhost:8080) | ``` User: admin``` <br> ``` Pass: password``` |         |
|Neo4j| **Database:** [http://localhost:7474](http://localhost:7474) | ``` User: neo4j``` <br> ``` Pass: password``` |         |
|MinIO| [http://localhost:9000](http://localhost:9000) | ``` User: admin``` <br> ``` Pass: password``` |           |
|FastAPI | [http://localhost:8000/docs](http://localhost:8000/docs)|  |         |
  

## References

[neo4j.com] (https://neo4j.com/docs/ogm-manual/current/reference/)

[uniprot.org] (https://www.uniprot.org/help/technical)

[airflow.apache.org] (https://airflow.apache.org/docs/apache-airflow/stable/)

[min.io] ([https://min.io/docs/minio/linux/developers/go/API.html](https://min.io/docs/minio/linux/reference/minio-server/minio-server.html)

