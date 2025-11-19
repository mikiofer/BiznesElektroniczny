FROM prestashop/prestashop:latest

# Set environment variables
ENV PS_INSTALL_AUTO=1
ENV PS_DEV_MODE=1
ENV DB_SERVER=db
ENV DB_NAME=prestashop
ENV DB_USER=root
ENV DB_PASS=root

# Copy custom configuration files if needed
COPY config/parameters.yml /var/www/html/app/config/parameters.yml

# Expose the port the app runs on
EXPOSE 80

# Start the application
CMD ["apache2-foreground"]