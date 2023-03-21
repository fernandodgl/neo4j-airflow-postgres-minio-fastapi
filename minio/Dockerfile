# # Base image
# FROM minio/minio:latest

# # Install MinIO client
# RUN wget https://dl.minio.io/client/mc/release/linux-amd64/mc -O /usr/local/bin/mc && \
#     chmod +x /usr/local/bin/mc

# # Create the bucket on MinIO server and run Flask app
# CMD mc alias set minio http://localhost:9000 minio minio123 --api S3v4 && \
#     mc mb --ignore-existing minio/uniprot-data && \
#     if [ $? -eq 0 ]; then echo "Bucket created successfully!"; else echo "Bucket creation failed!"; exit 1; fi && \
#     flask run --host=0.0.0.0 && \
#     rm /usr/local/bin/mc

FROM minio/minio:latest

# USER root

# FROM minio/minio:latest

# USER root

# COPY requirements.txt /requirements.txt

# RUN apk update && \
#     apk add --no-cache python3 py3-pip && \
#     pip3 install --no-cache-dir -r /requirements.txt

ENTRYPOINT ["minio"]
CMD ["server", "/data"]


ENTRYPOINT ["minio"]
CMD ["server", "/data"]
