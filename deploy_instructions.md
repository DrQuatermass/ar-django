# Deploy Instructions for VPS

## 1. Connetti al VPS via SSH
```bash
ssh root@94.177.171.193
# oppure ssh utente@ombradelportico.it
```

## 2. Installa le dipendenze di sistema
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv apache2 git
```

## 3. Crea directory per il progetto
```bash
cd /var/www
sudo mkdir ar_django
sudo chown $USER:$USER ar_django
cd ar_django
```

## 4. Clona il repository da GitHub
```bash
git clone https://github.com/TUO_USERNAME/ar_django.git .
# oppure se hai già pushato: git clone URL_REPO .
```

## 5. Crea ambiente virtuale e installa dipendenze
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 6. Configura Django
```bash
cd ar
python manage.py collectstatic --noinput
python manage.py migrate
```

## 7. Crea servizio systemd per Gunicorn
```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Incolla questo contenuto:
```
[Unit]
Description=gunicorn daemon for AR Django
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/ar_django/ar
Environment="PATH=/var/www/ar_django/venv/bin"
ExecStart=/var/www/ar_django/venv/bin/gunicorn --workers 3 --bind unix:/var/www/ar_django/ar.sock ar.wsgi:application

[Install]
WantedBy=multi-user.target
```

Salva e avvia Gunicorn:
```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn
```

## 8. Configura Apache2 come reverse proxy
```bash
sudo nano /etc/apache2/sites-available/ar_django.conf
```

Incolla questo contenuto:
```apache
<VirtualHost *:80>
    ServerName ombradelportico.it
    ServerAlias www.ombradelportico.it 94.177.171.193

    # Static files
    Alias /static/ /var/www/ar_django/ar/staticfiles/
    <Directory /var/www/ar_django/ar/staticfiles>
        Require all granted
    </Directory>

    # Media files
    Alias /media/ /var/www/ar_django/ar/media/
    <Directory /var/www/ar_django/ar/media>
        Require all granted
    </Directory>

    # Proxy to Gunicorn
    ProxyPreserveHost On
    ProxyPass /static/ !
    ProxyPass /media/ !
    ProxyPass / unix:/var/www/ar_django/ar.sock|http://ombradelportico.it/
    ProxyPassReverse / unix:/var/www/ar_django/ar.sock|http://ombradelportico.it/

    # Logs
    ErrorLog ${APACHE_LOG_DIR}/ar_django_error.log
    CustomLog ${APACHE_LOG_DIR}/ar_django_access.log combined
</VirtualHost>
```

Salva e attiva il sito:
```bash
sudo a2enmod proxy proxy_http
sudo a2ensite ar_django.conf
sudo a2dissite 000-default.conf
sudo apache2ctl configtest
sudo systemctl restart apache2
```

## 9. Configura HTTPS con Let's Encrypt
```bash
sudo apt install -y certbot python3-certbot-apache
sudo certbot --apache -d ombradelportico.it -d www.ombradelportico.it
```

Segui le istruzioni (inserisci email, accetta termini, etc.)

## 10. Verifica
Vai su https://ombradelportico.it - dovrebbe funzionare con HTTPS e il GPS dovrebbe chiedere i permessi!

## Comandi utili dopo il deploy

### Aggiornare il codice
```bash
cd /var/www/ar_django
git pull
source venv/bin/activate
pip install -r requirements.txt
cd ar
python manage.py collectstatic --noinput
python manage.py migrate
sudo systemctl restart gunicorn
sudo systemctl restart apache2
```

### Vedere i log
```bash
# Log Gunicorn
sudo journalctl -u gunicorn -f

# Log Apache
sudo tail -f /var/log/apache2/ar_django_error.log
sudo tail -f /var/log/apache2/ar_django_access.log
```

### Riavviare servizi
```bash
# Riavvia Gunicorn (dopo modifiche Python)
sudo systemctl restart gunicorn
sudo systemctl status gunicorn

# Riavvia Apache (dopo modifiche configurazione)
sudo systemctl restart apache2
sudo systemctl status apache2
```

### Debug
```bash
# Testa configurazione Apache
sudo apache2ctl configtest

# Verifica socket Gunicorn
ls -la /var/www/ar_django/ar.sock

# Testa Gunicorn manualmente
cd /var/www/ar_django/ar
source ../venv/bin/activate
gunicorn --bind 0.0.0.0:8000 ar.wsgi:application
```
