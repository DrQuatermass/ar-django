# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django 5.2.6 web application providing GPS-based Augmented Reality (AR) experiences. Users see virtual characters positioned in real-world locations using smartphone camera, GPS, and compass sensors.

## Development Setup

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Navigate to Django project
cd ar

# Run database migrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Access admin panel: http://127.0.0.1:8000/admin/
# Access AR camera: http://127.0.0.1:8000/
```

## Production Deployment

Deploy using **Gunicorn + Apache2** (reverse proxy) as documented in `deploy_instructions.md`.

**Architecture**: Apache2 serves static/media files directly and proxies Django requests to Gunicorn via Unix socket.

```bash
# Update code on server
cd /var/www/ar_django
git pull
source venv/bin/activate
pip install -r requirements.txt
cd ar
python manage.py collectstatic --noinput
python manage.py migrate
sudo systemctl restart gunicorn
sudo systemctl restart apache2

# View logs
sudo journalctl -u gunicorn -f              # Gunicorn application logs
sudo tail -f /var/log/apache2/ar_django_error.log   # Apache error logs

# Test configuration
sudo apache2ctl configtest                   # Apache config
ls -la /var/www/ar_django/ar.sock           # Gunicorn socket

# Restart services
sudo systemctl restart gunicorn             # After Python code changes
sudo systemctl restart apache2              # After Apache config changes
```

**Stack**: Apache2 (reverse proxy + static files) → Gunicorn (WSGI server) → Django

## Architecture

### AR Positioning System (Hybrid Three-Tier)

**Priority-based positioning with sensor fusion:**

1. **GPS + Compass** → Initial detection and coarse positioning
   - Haversine formula calculates distance to character GPS coordinates
   - Characters activate within `activation_distance` meters
   - Compass bearing determines screen position within FOV

2. **Dual-Marker Detection** → High-precision positioning at short range
   - **Detection Marker** (100+ matches): Decides WHETHER to show character
   - **Positioning Marker** (40+ matches): Decides WHERE to position character
   - OpenCV.js ORB feature detection with outlier filtering
   - Pixel-perfect offset from detected marker

3. **Screen Anchoring** → Stability when marker lost
   - Created when positioning marker reaches 40+ matches
   - Stores: `{screenX, screenY, relativeBearing, distance, cameraHeading}`
   - Character remains anchored in 3D space, adjusts for camera rotation only
   - **Does NOT use GPS** (prevents drift after anchor creation)

**Positioning Priority** (`camera.html` ~line 1400):
```
if (positioningMarker detected):
    → Real-time marker tracking
else if (worldAnchor exists):
    → Screen anchor (heading-adjusted, GPS-independent)
else if (detectionMarker detected AND no anchor):
    → Detection marker fallback
else:
    → Hide character
```

### Kalman Filtering (Sensor Smoothing)

All sensor inputs filtered to reduce noise:

- **GPS (lat/lng)**: `KalmanFilter(q=0.001, r=0.5)`
  - Reduces ±10m jitter from GPS inaccuracy

- **Compass (heading)**: `KalmanFilter(q=0.05, r=0.3)`
  - Handles circular wraparound (359°→1°)
  - Reduces bearing oscillation

Filters in `camera.html` starting line ~362.

### Database Schema

**CharConfiguration Model** (`home/models.py`):
- GPS: `target_latitude`, `target_longitude`, `activation_distance`
- 3D positioning: `altitude`, `height_offset`, `base_size`, `facing_direction`, `display_mode`
- Assets: `character_image`, `marker_image`, `positioning_marker_image`
- Marker offsets: `marker_offset_x`, `marker_offset_y`, `marker_offset_z`
- Mode: `use_marker` (enables dual-marker vs pure GPS)

### Frontend Architecture

**Main template**: `ar/home/templates/home/camera.html` (~1700 lines)

**Key JavaScript classes:**
- `KalmanFilter`: Sensor noise reduction
- `ARCamera`: Main controller
  - `initCamera()`: Camera stream
  - `initGPS()`: GPS with Kalman filtering
  - `initOrientation()`: Compass with Kalman filtering
  - `initMarkerDetection()`: OpenCV.js + ORB detection loop
  - `createWorldAnchor()`: Screen-relative anchor creation
  - `worldToScreen()`: GPS→screen coordinates (non-marker mode)
  - `createOrUpdateARCharacter()`: Main rendering with priority logic

**Data flow:**
1. Characters embedded via `window.EMBEDDED_CHARACTERS` (zero latency)
2. Fallback API: `/api/characters/`
3. Video frame → OpenCV ORB → Match filtering → Position calc → DOM update

### Marker Detection Implementation

**Two-marker system** (optional per character):

| Marker Type | Threshold | Purpose |
|-------------|-----------|---------|
| Detection | 100+ matches | IF character visible |
| Positioning | 40+ for anchor, lower for tracking | WHERE to position |

**ORB Configuration** (line ~470):
- nfeatures: 1000 (detection) / 500 (positioning)
- Outlier filter: Median ± 20%
- Temporal persistence: 5 frames after marker loss

### Critical Implementation Details

1. **Anchor Creation**: Only when `positioningMarker.matches >= 40` AND GPS+compass available (line ~878)

2. **Circular Math**: Heading wraparound handling:
   ```javascript
   let diff = newHeading - oldHeading;
   if (diff > 180) diff -= 360;
   if (diff < -180) diff += 360;
   ```

3. **Coordinate Spaces**:
   - Marker coords: video space (videoWidth × videoHeight)
   - Must scale to: screen space (innerWidth × innerHeight)

4. **FOV Culling**: 70° horizontal FOV, cull outside ±35° from heading

5. **Distance Scaling**: Inverse proportional, clamped [0.5, 2.0]

## Important Constraints

- **HTTPS Required**: GPS/camera permissions require HTTPS (localhost exempt)
- **Mobile-First**: Designed for smartphone sensors
- **OpenCV.js**: ~8MB library, async loading with status indicator
- **iOS Compass**: Requires `DeviceOrientationEvent.requestPermission()` via button
- **GPS Accuracy**: Real-world ±10-24m, hence marker precision needed at close range

## Configuration

- `settings.py`: Update `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` for production
- Static: Collected to `staticfiles/` for Apache serving
- Media: Uploads to `media/characters/` and `media/markers/`
- Database: SQLite (dev), PostgreSQL recommended (production scale)

## Testing Characters

Admin panel (`/admin/`) → Create `CharConfiguration`:
1. Set GPS coords (Google Maps for accuracy)
2. Upload character PNG (transparency supported)
3. Optional: Upload marker images for precision
4. Set `activation_distance` (50-100m for testing)
5. Configure offsets if using markers

## Known Limitations

- GPS drift affects initial detection (Kalman mitigates)
- Compass varies by device (magnetic interference)
- Marker detection needs good lighting + stable camera
- World anchoring assumes flat terrain
- No multi-user sync (each client independent)
