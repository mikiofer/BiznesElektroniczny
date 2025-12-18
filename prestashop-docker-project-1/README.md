# Projekt PrestaShop z Docker (środowisko developerskie)

Ten projekt uruchamia środowisko PrestaShop przy użyciu Dockera i Docker Compose. Zawiera podstawowe pliki konfiguracyjne, które pozwalają szybko wystartować sklep z bazą danych.

## Struktura projektu

- docker-compose.yml        — definicja usług (PrestaShop, baza danych, nginx itp.)
- .env.example              — przykładowe zmienne środowiskowe, skopiuj do `.env`
- .gitignore                — pliki/folery ignorowane przez Git
- prestashop/               — miejsce na pliki sklepu, moduły, motywy
  - Dockerfile              — (opcjonalny) budowa obrazu PrestaShop
  - config/                 — pliki konfiguracyjne PrestaShop
  - modules/                — katalog modułów
  - themes/                 — katalog motywów
- db/init/init.sql          — (opcjonalnie) skrypty inicjalizacyjne bazy
- nginx/                    — konfiguracja reverse-proxy / SSL
- scripts/                  — skrypty pomocnicze (setup, backup)

## Przygotowanie i uruchomienie (Windows)

1. Zainstaluj Docker Desktop z włączonym WSL2 i uruchom Docker.
2. Otwórz PowerShell / Git Bash / WSL i przejdź do katalogu projektu:
   cd "c:\Users\mikis\Documents\BiznesElektroniczny\BiznesElektroniczny\prestashop-docker-project\prestashop-docker-project"
3. Skopiuj plik z przykładowymi zmiennymi:
   - PowerShell: `copy .env.example .env`
   - Git Bash/WSL: `cp .env.example .env`
   Edytuj `.env` i dostosuj porty/hasła jeśli potrzebne.
4. Uruchom kontenery:
   - `docker compose up -d --build`  (lub `docker-compose up -d --build`)
5. Sprawdź uruchomione kontenery:
   - `docker compose ps`  lub `docker ps`
6. Otwórz przeglądarkę na adresie `http://localhost:<PORT>` (porty sprawdź w docker compose lub w output `docker ps`).

## Uwaga o PrestaShop
- Nie trzeba ręcznie instalować plików PrestaShop — Docker pobierze obraz i uruchomi instalator. Jeśli chcesz trzymać kod sklepu w repozytorium (np. motyw, moduły), umieść go w katalogu `prestashop/` i skonfiguruj docker-compose, aby był montowany do kontenera.

## Debug / logi / zatrzymanie
- Logi: `docker compose logs -f prestashop`
- Zatrzymanie: `docker compose down`

## Zespół
