# Deploy Instructions for VPS

## 1. Connetti al VPS via SSH
```bash
ssh root@94.177.171.193
# oppure ssh utente@ombradelportico.it
```

## 2. Installa le dipendenze di sistema
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv apache2 libapache2-mod-wsgi-py3 git
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

## 7. Configura permessi per Apache
```bash
sudo chown -R www-data:www-data /var/www/ar_django
sudo chmod -R 755 /var/www/ar_django
```

## 8. Configura Apache2
```bash
sudo nano /etc/apache2/sites-available/ar_django.conf
```

Incolla questo contenuto:
```apache
<VirtualHost *:80>
    ServerName ombradelportico.it
    ServerAlias www.ombradelportico.it 94.177.171.193

    # Django application
    WSGIDaemonProcess ar_django python-home=/var/www/ar_django/venv python-path=/var/www/ar_django/ar
    WSGIProcessGroup ar_django
    WSGIScriptAlias / /var/www/ar_django/ar/ar/wsgi.py

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

    # WSGI configuration
    <Directory /var/www/ar_django/ar/ar>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>

    # Logs
    ErrorLog ${APACHE_LOG_DIR}/ar_django_error.log
    CustomLog ${APACHE_LOG_DIR}/ar_django_access.log combined
</VirtualHost>
```

Salva e attiva il sito:
```bash
sudo a2ensite ar_django.conf
sudo a2enmod wsgi
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
sudo systemctl restart apache2
```

### Vedere i log
```bash
sudo tail -f /var/log/apache2/ar_django_error.log
sudo tail -f /var/log/apache2/ar_django_access.log
```

### Riavviare Apache
```bash
sudo systemctl restart apache2
sudo systemctl status apache2
```

### Testare configurazione Apache
```bash
sudo apache2ctl configtest
```
