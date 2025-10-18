# Deploy Instructions for VPS

## 1. Connetti al VPS via SSH
```bash
ssh root@94.177.171.193
# oppure ssh utente@ombradelportico.it
```

## 2. Installa le dipendenze di sistema
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx git
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

## 7. Testa Gunicorn
```bash
gunicorn --bind 0.0.0.0:8000 ar.wsgi:application
# Premi CTRL+C per fermare, poi prosegui
```

## 8. Crea servizio systemd per Gunicorn
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

Salva (CTRL+O, ENTER, CTRL+X)

```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn
```

## 9. Configura Nginx
```bash
sudo nano /etc/nginx/sites-available/ar_django
```

Incolla questo contenuto:
```
server {
    listen 80;
    server_name ombradelportico.it www.ombradelportico.it 94.177.171.193;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /var/www/ar_django/ar/staticfiles/;
    }

    location /media/ {
        alias /var/www/ar_django/ar/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/ar_django/ar.sock;
    }
}
```

Salva e attiva:
```bash
sudo ln -s /etc/nginx/sites-available/ar_django /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 10. Configura HTTPS con Let's Encrypt
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d ombradelportico.it -d www.ombradelportico.it
```

Segui le istruzioni (inserisci email, accetta termini, etc.)

## 11. Verifica
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
```

### Vedere i log
```bash
sudo journalctl -u gunicorn
sudo tail -f /var/log/nginx/error.log
```

### Riavviare servizi
```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```
