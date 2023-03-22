#!/bin/bash
set -e
apt-get update && apt-get upgrade
# Initialize the database
airflow db init

# Create a default user if it doesn't exist
airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname Admin \
    --role Admin \
    --email admin@example.com || true

# Start the scheduler and webserver in the background


airflow scheduler &
airflow webserver

# Keep the script running
tail -f /dev/null


