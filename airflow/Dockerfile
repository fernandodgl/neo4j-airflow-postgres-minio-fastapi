FROM apache/airflow:2.2.3

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


COPY entrypoint.sh /entrypoint.sh

USER root
RUN echo "deb http://deb.debian.org/debian stretch main" >> /etc/apt/sources.list
RUN echo "deb http://security.debian.org/debian-security stretch/updates main" >> /etc/apt/sources.list
RUN apt-get update && apt-get install -y --no-install-recommends openjdk-8-jdk && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN chmod +x /entrypoint.sh
USER airflow

COPY dags /opt/airflow/dags

ENTRYPOINT ["/entrypoint.sh"]


# USER root
# RUN apt-get update && apt-get install -y openjdk-8-jdk
# RUN chmod +x /entrypoint.sh
# USER airflow

# COPY dags /opt/airflow/dags

# ENTRYPOINT ["/entrypoint.sh"]

