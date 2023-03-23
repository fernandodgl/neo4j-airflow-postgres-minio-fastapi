#!/bin/bash

set -e

# Upload a file to the bucket
mc anonymous policy set public minio/bucket;
mc mc anonymous cp -r ./data/Q9Y261.xml minio/bucket/
# cp $file_path /var/lib/docker/volumes/minio-data/_data

