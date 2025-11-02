#!/bin/bash

# Define backup directory
BACKUP_DIR="./backups"
DATE=$(date +"%Y%m%d_%H%M%S")

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Backup database
docker exec prestashop-docker-project_db_1 /usr/bin/mysqldump -u root --password=root prestashop > $BACKUP_DIR/db_backup_$DATE.sql

# Backup PrestaShop files
tar -czf $BACKUP_DIR/prestashop_backup_$DATE.tar.gz ./prestashop

echo "Backup completed successfully!"