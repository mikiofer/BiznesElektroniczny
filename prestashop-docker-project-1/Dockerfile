# Bazujemy na oficjalnym obrazie PrestaShop (zmień wersję jeśli używasz innej, np. 8.1)
FROM prestashop/prestashop:1.7.8

# Kopiujemy wygenerowane certyfikaty do wnętrza kontenera
COPY ./certs/server.crt /etc/apache2/ssl/server.crt
COPY ./certs/server.key /etc/apache2/ssl/server.key

# Kopiujemy konfigurację SSL dla Apache
COPY ./ssl.conf /etc/apache2/sites-available/default-ssl.conf

# Włączamy moduł SSL w Apache i aktywujemy naszą konfigurację
RUN a2enmod ssl && a2ensite default-ssl