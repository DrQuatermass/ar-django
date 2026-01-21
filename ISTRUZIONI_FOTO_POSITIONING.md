# 📸 Come Scattare il Positioning Marker Corretto

## ✅ Foto Corretta: Close-up CASSETTIERA

### Cosa Fotografare:
```
┌─────────────────────────────────┐
│                                 │
│    [Cassettiera - Piano Top]   │ ← Inquadra questo
│                                 │
│    [Cassetto superiore]        │
│    ○────────────○               │ ← Maniglie visibili
│                                 │
│    [Parte cassetto medio]      │
│                                 │
└─────────────────────────────────┘
```

### Istruzioni Scatto:

**1. Posizione:**
- Distanza: 80cm - 1 metro dalla cassettiera
- Altezza: Occhi allineati con piano top della cassettiera
- Angolazione: FRONTALE (90° rispetto al mobile)

**2. Inquadratura:**
- Piano top cassettiera deve riempire 60% del frame
- Includi cassetto superiore con maniglie
- NON fotografare la pianta (o minima parte)
- Focus su texture legno + maniglie

**3. Scatto:**
- Luce: naturale dalla finestra (come foto ambiente)
- Messa a fuoco: AUTO su maniglia centrale
- Formato: JPEG/PNG, risoluzione minima 1200x900px
- NO flash, NO HDR, NO filtri

**4. Verifica Qualità:**
- Texture legno nitida ✓
- Maniglie a fuoco ✓
- Nessuna sfocatura ✓
- Buon contrasto ✓

## 📐 Configurazione Offset dopo Nuova Foto

Con positioning marker = PIANO TOP CASSETTIERA:

```python
# Origin (0,0,0) = CENTRO PIANO TOP CASSETTIERA

marker_offset_x = 0.3    # 30cm a DESTRA (dove sta la pianta)
marker_offset_y = 0.9    # 90cm SOPRA piano cassettiera
marker_offset_z = 0.0    # Allineato profondità

# Risultato: Character in piedi accanto alla pianta
# (la pianta è 30cm a destra del centro cassettiera)
```

## 🎯 Visualizzazione:

```
Vista dall'alto:
═══════════════

        👤 Character
        │
   [Cassettiera] ──→ 30cm → 🌿 Pianta
        ↑
     marker
   (piano top)


Vista laterale:
═══════════════

     👤 Character
     │  ← 90cm sopra
   ──┴──
   [═══]  Piano top (marker origin)
   [═══]  Cassetto 1
   [═══]  Cassetto 2
   [═══]  Cassetto 3
```

## ⚙️ Admin Panel Settings

```python
positioning_marker_image = "cassettiera_top_closeup.jpg"

marker_offset_x = 0.3    # Character vicino alla pianta (30cm destra)
marker_offset_y = 0.9    # Character in piedi (90cm sopra piano)
marker_offset_z = 0.2    # Leggermente avanti (20cm)

base_size = 1.0
display_mode = "standing"
```

## 🧪 Test Atteso

1. Inquadra ambiente → Detection OK (156 matches)
2. Avvicinati e inquadra CASSETTIERA TOP → Positioning (80+ matches expected)
3. Anchor creato → Character appare vicino alla pianta
4. Gira camera → Character resta ancorato in 3D

## 📊 Features Attese

```
Console output:
"Loaded detection marker: 856 features" ✓
"Loaded positioning marker: 1200+ features" ✓ (cassettiera)
vs
"Loaded positioning marker: 300 features" ✗ (pianta - troppo poche)
```

---

**IMPORTANTE:**
- Fotografa CASSETTIERA, non pianta
- Usa cassettiera come anchor point stabile
- Offset sposta character verso la pianta
