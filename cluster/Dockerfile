# bazujemy na oficjalnym obrazie PrestaShop
FROM prestashop/prestashop:1.7.8

# kopiujemy wygenerowane certyfikaty do wnętrza kontenera
COPY ./certs/server.crt /etc/apache2/ssl/server.crt
COPY ./certs/server.key /etc/apache2/ssl/server.key

# kopiujemy konfigurację SSL dla Apache
COPY ./ssl.conf /etc/apache2/sites-available/default-ssl.conf

# zdjecia i slider prestashop
COPY ./prestashop/img/ /var/www/html/img/
COPY ./prestashop/modules/ps_imageslider/images/ /var/www/html/modules/ps_imageslider/images/

# parameters.php
COPY ./prestashop/app/config/parameters.php /var/www/html/app/config/parameters.php

# uprawnienia + ssl
RUN a2enmod ssl \
 && a2ensite default-ssl \
 && chown -R www-data:www-data /var/www/html/img /var/www/html/modules/ps_imageslider/images /var/www/html/app/config/parameters.php

 #brak install
 RUN rm -rf /var/www/html/install /var/www/html/install-dev
