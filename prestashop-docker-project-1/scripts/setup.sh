#!/bin/bash

# Navigate to the project directory
cd "$(dirname "$0")/.."

# Build the Docker images
docker-compose build

# Start the Docker containers
docker-compose up -d

# Wait for the database to be ready
echo "Waiting for the database to be ready..."
until docker-compose exec db mysqladmin --user=root --password=root ping; do
    sleep 2
done

# Initialize the database
echo "Initializing the database..."
docker-compose exec db mysql -u root -proot < db/init/init.sql

echo "Setup completed. PrestaShop is now running."