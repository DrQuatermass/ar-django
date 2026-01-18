# Deploy Simple Mode in Produzione

## Comandi da eseguire sul server

```bash
# 1. Naviga alla directory del progetto
cd /var/www/ar_django

# 2. Pull del nuovo codice
git pull

# 3. Attiva virtual environment
source venv/bin/activate

# 4. Naviga alla directory Django
cd ar

# 5. Raccogli static files (se ce ne sono di nuovi)
python manage.py collectstatic --noinput

# 6. IMPORTANTE: Aggiorna il database per aggiungere positioning_marker_image
python manage.py shell -c "
from home.models import CharConfiguration
char = CharConfiguration.objects.get(id=1)  # Alberto Pio
char.positioning_marker_image = char.marker_image  # Usa lo stesso marker
char.save()
print(f'Aggiornato {char.name}: positioning_marker={char.positioning_marker_image}')
"

# 7. Restart Gunicorn per caricare nuovo codice
sudo systemctl restart gunicorn

# 8. Restart Apache (opzionale, solo se hai problemi)
sudo systemctl restart apache2

# 9. Verifica che i servizi siano attivi
sudo systemctl status gunicorn
sudo systemctl status apache2
```

## Verifica

1. Apri nel browser: `https://tuodominio.com/simple/`
2. Dovresti vedere:
   - "OpenCV: Pronto"
   - "Personaggi: 1"
   - La camera dovrebbe attivarsi

3. Per testare il marker:
   - Apri `https://tuodominio.com/media/markers/IMG_3946.jpeg` su un altro schermo
   - Inquadra il marker con la camera
   - Il personaggio Alberto Pio dovrebbe apparire sopra il marker

## Troubleshooting

### Errore: "Nessun personaggio con positioning marker"
```bash
# Verifica che il database sia aggiornato
cd /var/www/ar_django/ar
source ../venv/bin/activate
python manage.py shell -c "
from home.models import CharConfiguration
chars = CharConfiguration.objects.filter(positioning_marker_image__isnull=False)
print(f'Personaggi con positioning marker: {chars.count()}')
for c in chars:
    print(f'- {c.name}: {c.positioning_marker_image}')
"
```

### Errore 500 o pagina non carica
```bash
# Controlla i log
sudo journalctl -u gunicorn -n 50 -f
```

### Static files non caricano
```bash
# Riesegui collectstatic e controlla permessi
cd /var/www/ar_django/ar
source ../venv/bin/activate
python manage.py collectstatic --noinput
sudo chown -R www-data:www-data /var/www/ar_django/staticfiles/
```

## Note Importanti

- La modalità `/simple/` è **completamente indipendente** dalla modalità originale `/`
- Entrambe possono coesistere senza problemi
- Se un personaggio non ha `positioning_marker_image`, non apparirà in `/simple/`
- La modalità original `/` continua a funzionare normalmente con GPS+marker

## Testing Rapido

Dopo il deploy, testa rapidamente con:
```bash
curl https://tuodominio.com/simple/ | grep "window.EMBEDDED_CHARACTERS"
```

Dovrebbe mostrare i dati JSON dei personaggi con positioning marker.
