# Bazujemy na oficjalnym obrazie PrestaShop (zmień wersję jeśli używasz innej, np. 8.1)
FROM prestashop/prestashop:1.7.8

# Kopiujemy wygenerowane certyfikaty do wnętrza kontenera
COPY ./certs/server.crt /etc/apache2/ssl/server.crt
COPY ./certs/server.key /etc/apache2/ssl/server.key

# Kopiujemy konfigurację SSL dla Apache
COPY ./ssl.conf /etc/apache2/sites-available/default-ssl.conf

# Twoje pliki PrestaShop (zdjęcia + slider)
COPY ./prestashop/img/ /var/www/html/img/
COPY ./prestashop/modules/ps_imageslider/images/ /var/www/html/modules/ps_imageslider/images/

# parameters.php (jeśli chcesz go mieć od razu)
COPY ./prestashop/app/config/parameters.php /var/www/html/app/config/parameters.php

#
# Włączamy moduł SSL w Apache i aktywujemy naszą konfigurację
#RUN a2enmod ssl && a2ensite default-ssl
#
# uprawnienia + ssl
RUN a2enmod ssl \
 && a2ensite default-ssl \
 && chown -R www-data:www-data /var/www/html/img /var/www/html/modules/ps_imageslider/images /var/www/html/app/config/parameters.php

 #brak install
 RUN rm -rf /var/www/html/install /var/www/html/install-dev
