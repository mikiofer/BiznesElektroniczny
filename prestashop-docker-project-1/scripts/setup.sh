#!/bin/bash
cd "$(dirname "$0")/.."

# Build i uruchom
docker compose up -d --build

# Czekaj na DB (root password zgodny z docker-compose.yml)
echo "Waiting for database..."
until docker compose exec db mysqladmin --user=root --password=root_password ping &>/dev/null; do
  sleep 2
done

echo "Database ready."
# Nie uruchamiamy ręcznej inicjalizacji jeśli zostawiasz instalator PrestaShop
echo "Setup completed. PrestaShop jest uruchomiony."