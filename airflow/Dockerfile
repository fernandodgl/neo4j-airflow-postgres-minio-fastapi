FROM apache/airflow:2.2.3

#FROM apache/airflow:2.5.3

COPY entrypoint.sh /entrypoint.sh

USER root
RUN chmod +x /entrypoint.sh
USER airflow

COPY dags /opt/airflow/dags

ENTRYPOINT ["/entrypoint.sh"]
