#!/bin/bash
set -e
SUDO apt-get update && apt-get upgrade
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


### TEST
#!/bin/bash
# entrypoint.sh

# Apply database migrations
#echo "Applying database migrations..."
#airflow db upgrade

# Create an admin user
#echo "Creating an admin user..."
#airflow users create --username admin --password admin --firstname admin --lastname admin --role Admin --email admin@example.com

# Start the web server, with "-p 8080" flag to set the port
#echo "Starting the web server on port 8080..."
#exec airflow webserver -p 8080
