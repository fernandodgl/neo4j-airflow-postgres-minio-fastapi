FROM apache/airflow:2.2.3

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY entrypoint.sh /entrypoint.sh

USER root
RUN chmod +x /entrypoint.sh
USER airflow

COPY dags /opt/airflow/dags

ENTRYPOINT ["/entrypoint.sh"]
