#!/bin/bash
set -e

# Wait for Minio server to start
until curl -sSf http://localhost:9000; do
  echo 'Waiting for Minio server to start...'
  sleep 1
done

# Create bucket if it doesn't exist
mc config host add uniprot http://localhost:9000 minio minio123
if ! mc ls uniprot/uniprot-data &> /dev/null; then
  mc mb uniprot/uniprot-data
fi
