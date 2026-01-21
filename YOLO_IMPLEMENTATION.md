# YOLO Object Detection Implementation

## Overview

Implementazione di object detection basata su YOLO per AR positioning. Il sistema rileva oggetti reali (bottiglia, sedia, laptop, ecc.) e posiziona i character AR in modo persistente.

## Architettura

### One-Shot Detection + Persistent Anchors

```
User → GPS area → Character activated → YOLO detection (1x) → Fixed anchor → Character visible
```

**Vantaggi:**
- ✅ Detection server-side: funziona su TUTTI i device
- ✅ Latency iniziale 500ms accettabile (solo 1 volta)
- ✅ Zero processing dopo detection (batteria OK)
- ✅ Character stabile (no jitter)
- ✅ Scalabile (server GPU opzionale)

## Setup

### 1. Installa dipendenze

```bash
pip install -r requirements.txt
```

Questo installerà `ultralytics==8.0.200` che include YOLOv8.

### 2. Download modello YOLO

Il modello `yolov8n.pt` (nano, ~6MB) viene scaricato automaticamente al primo avvio del server.

```bash
cd ar
python manage.py runserver
```

Al primo accesso a `/yolo/` o chiamata API `/api/yolo-detect/`, il modello verrà scaricato in `~/.cache/ultralytics/`.

### 3. Esegui migration

```bash
cd ar
python manage.py migrate
```

Questo crea i nuovi campi nel database:
- `use_yolo_detection` (Boolean)
- `yolo_object_class` (String)
- `yolo_confidence_threshold` (Float)

## Configurazione Character

### Admin Panel

1. Vai su `/admin/`
2. Seleziona un Character o creane uno nuovo
3. Configura:

**GPS (obbligatorio):**
- `target_latitude`: latitudine area
- `target_longitude`: longitudine area
- `activation_distance`: raggio in metri (es: 50)

**YOLO Object Detection:**
- ✅ `use_yolo_detection`: Abilita detection YOLO
- `yolo_object_class`: Classe oggetto (es: "bottle", "chair", "laptop")
- `yolo_confidence_threshold`: Soglia minima (default: 0.5 = 50%)

**Opzionale:**
- `marker_offset_x/y`: Offset dal punto di detection in metri
- `base_size`: Scala immagine character

### Classi YOLO Disponibili - Oggetti FISSI per Negozi/Spazi Urbani

**OGGETTI CONSIGLIATI** (statici, sempre nella stessa posizione):

**Arredamento:**
- `chair` - Sedia (perfetto per bar, ristoranti, negozi)
- `couch` - Divano (negozi arredamento, sale d'attesa)
- `bench` - Panchina (spazi pubblici, parchi)
- `dining table` - Tavolo (ristoranti, negozi)
- `bed` - Letto (negozi arredamento)

**Elettrodomestici:**
- `refrigerator` - Frigorifero (negozi elettrodomestici, bar)
- `microwave` - Microonde (negozi, cucine)
- `oven` - Forno (negozi, panetterie)
- `toaster` - Tostapane
- `sink` - Lavandino
- `toilet` - Toilette

**Elettronica:**
- `tv` - Televisore (negozi elettronica, vetrine)
- `laptop` - Computer portatile (negozi informatica)
- `clock` - Orologio (gioiellerie, negozi)

**Decorazioni:**
- `potted plant` - Pianta in vaso (molto comune ovunque!)
- `vase` - Vaso decorativo
- `book` - Libro (librerie, biblioteche)

**Display/Vetrine:**
- `bottle` - Bottiglia (farmacie, enoteche, negozi)
- `wine glass` - Bicchiere da vino (ristoranti, bar)
- `cup` - Tazza (bar, caffetterie)

**EVITA** oggetti mobili: person, car, bicycle, backpack, cell phone, handbag, ecc.

**Lista completa 80 oggetti COCO** (reference):
```
person, bicycle, car, motorcycle, airplane, bus, train, truck, boat,
traffic light, fire hydrant, stop sign, parking meter, bench, bird, cat, dog,
horse, sheep, cow, elephant, bear, zebra, giraffe, backpack, umbrella, handbag,
tie, suitcase, frisbee, skis, snowboard, sports ball, kite, baseball bat,
baseball glove, skateboard, surfboard, tennis racket, bottle, wine glass, cup,
fork, knife, spoon, bowl, banana, apple, sandwich, orange, broccoli, carrot,
hot dog, pizza, donut, cake, chair, couch, potted plant, bed, dining table,
toilet, tv, laptop, mouse, remote, keyboard, cell phone, microwave, oven,
toaster, sink, refrigerator, book, clock, vase, scissors, teddy bear, hair drier,
toothbrush
```

## Uso

### URL Endpoint

**Camera YOLO:**
```
http://localhost:8000/yolo/
```

**API Detection (interno):**
```
POST /api/yolo-detect/
Content-Type: application/json

{
  "image": "data:image/jpeg;base64,...",
  "object_class": "bottle",
  "confidence_threshold": 0.5
}

Response:
{
  "success": true,
  "detections": [
    {
      "class": "bottle",
      "confidence": 0.87,
      "bbox": {"x": 640, "y": 360, "w": 120, "h": 250}
    }
  ],
  "count": 1
}
```

### Workflow Utente

1. **Apri** `http://localhost:8000/yolo/` su smartphone
2. **Permetti** accesso camera e GPS
3. **Entra** nell'area GPS configurata
4. **Inquadra** l'oggetto configurato (es: bottiglia)
5. **Attendi** ~500ms per detection server
6. **Character appare** ancorato all'oggetto
7. **Character rimane** fisso anche muovendo camera

## Performance

### Server

**CPU (senza GPU):**
- Detection: 300-800ms
- YOLOv8n model: ~6MB
- RAM usage: ~200MB

**Con GPU CUDA:**
- Detection: 50-150ms
- Molto più accurato

### Client

**Prima detection:**
- Upload frame: 100-200ms (dipende da connessione)
- Detection server: 300-800ms
- Totale: ~500-1000ms

**Dopo detection:**
- CPU: 0% (character fisso)
- RAM: ~10MB per character
- Batteria: impatto minimo

## Troubleshooting

### Modello YOLO non si carica

```python
# Verifica installazione ultralytics
pip show ultralytics

# Test manuale caricamento
from ultralytics import YOLO
model = YOLO('yolov8n.pt')
print("Model loaded successfully")
```

### Detection sempre fallisce

1. **Verifica classe corretta:**
   - Usa nome esatto dalla lista (es: "bottle" non "water_bottle")

2. **Abbassa threshold:**
   - Prova `yolo_confidence_threshold = 0.3` invece di 0.5

3. **Check illuminazione:**
   - YOLO funziona meglio con buona luce

4. **Oggetto troppo lontano:**
   - Avvicina smartphone all'oggetto

### Performance lente

**Server CPU:**
- Usa YOLOv8n (nano) - già configurato
- Considera GPU server per produzione

**Network slow:**
- Riduci qualità JPEG nel client:
  ```javascript
  canvas.toDataURL('image/jpeg', 0.6)  // era 0.8
  ```

## Production Deployment

### Con GPU (raccomandato)

```bash
# Server con NVIDIA GPU
pip install ultralytics[gpu]

# Verifica CUDA
python -c "import torch; print(torch.cuda.is_available())"
```

YOLO userà automaticamente GPU se disponibile → 5-10x più veloce.

### Senza GPU

YOLOv8n funziona anche su CPU normale, performance accettabili per one-shot detection.

### Scaling

**Carico server:**
- 1 detection = ~300-800ms CPU
- 100 utenti/ora = ~50 secondi CPU/ora
- Server medio gestisce facilmente

**Cache (opzionale):**
Per scene fisse (es: stessa bottiglia sempre lì), considera caching delle detection per ridurre load.

## Confronto con Marker System

| Feature | Marker (ORB) | YOLO Objects |
|---------|--------------|--------------|
| **Setup** | Foto marker richiesta | Solo seleziona classe |
| **Robustness** | Sensibile a angolazione | Riconosce da ogni lato |
| **Performance** | Client-side (rapido) | Server-side (~500ms) |
| **Battery** | Alta (processing continuo) | Bassa (one-shot) |
| **Accuracy** | Ottima se marker visibile | Buona, dipende da oggetto |
| **Oggetti** | Qualsiasi foto | Solo 80 classi COCO |
| **Use case** | Marker stampati/fissi | Oggetti reali comuni |

**Conclusione:** YOLO perfetto per oggetti comuni (bottiglie, sedie, ecc.), Marker meglio per scene personalizzate.

## Next Steps

### Possibili Miglioramenti

1. **Refresh anchor (opzionale):**
   ```javascript
   // Ri-detection ogni 30 secondi per correggere drift
   setInterval(() => {
     if (anchor.age > 30000) detectAndAnchor(char);
   }, 5000);
   ```

2. **Multi-instance:**
   Se più bottiglie, seleziona quella più vicina a reference point.

3. **Custom training:**
   Train YOLOv8 su oggetti specifici non in COCO dataset.

4. **Confidence display:**
   Mostra % confidenza nel debug panel.

## Support

Per problemi o domande:
- Check logs: `sudo journalctl -u gunicorn -f`
- Django logs: `/var/log/django/`
- YOLO errors: stampati in console server
