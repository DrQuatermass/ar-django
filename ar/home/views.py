from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from .models import CharConfiguration
import json
import base64
import cv2
import numpy as np
from PIL import Image
import io

# YOLO model - caricato una sola volta all'avvio
_yolo_model = None

def get_yolo_model():
    """Lazy loading del modello YOLO"""
    global _yolo_model
    if _yolo_model is None:
        try:
            from ultralytics import YOLO
            _yolo_model = YOLO('yolov8n.pt')  # YOLOv8 nano (più leggero)
            print("YOLO model loaded successfully")
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            _yolo_model = False  # Segna come fallito per non ritentare
    return _yolo_model if _yolo_model is not False else None

# Create your views here.

def camera_view(request):
    """
    View per la fotocamera AR con bussola e GPS
    """
    # Ottieni tutte le configurazioni dei personaggi
    characters = CharConfiguration.objects.all()

    # Serializza i dati per embedding diretto nell'HTML
    character_data = []
    for char in characters:
        data = {
            'id': char.id,
            'name': char.name,
            'target_latitude': char.target_latitude,
            'target_longitude': char.target_longitude,
            'activation_distance': char.activation_distance,
            'character_image': char.character_image.url if char.character_image else None,
            'altitude': char.altitude,
            'height_offset': char.height_offset,
            'base_size': char.base_size,
            'facing_direction': char.facing_direction,
            'display_mode': char.display_mode,
            'use_marker': char.use_marker,
            'marker_image': char.marker_image.url if char.marker_image else None,
            'positioning_marker_image': char.positioning_marker_image.url if char.positioning_marker_image else None,
            'marker_offset_x': char.marker_offset_x,
            'marker_offset_y': char.marker_offset_y,
            'marker_offset_z': char.marker_offset_z,
            'detection_marker_features': char.detection_marker_features,
            'positioning_marker_features': char.positioning_marker_features,
        }
        character_data.append(data)

    context = {
        'characters': characters,
        'characters_json': json.dumps(character_data),  # Embedded JSON
    }

    return render(request, 'home/camera.html', context)

def camera_simple_view(request):
    """
    View per la fotocamera AR semplificata (solo marker-based positioning)
    """
    # Ottieni solo i personaggi con positioning_marker_image
    characters = CharConfiguration.objects.filter(positioning_marker_image__isnull=False).exclude(positioning_marker_image='')

    # Serializza i dati per embedding diretto nell'HTML
    character_data = []
    for char in characters:
        data = {
            'id': char.id,
            'name': char.name,
            'character_image': char.character_image.url if char.character_image else None,
            'positioning_marker_image': char.positioning_marker_image.url,
            'base_size': char.base_size,
            'marker_offset_x': char.marker_offset_x,
            'marker_offset_y': char.marker_offset_y,
        }
        character_data.append(data)

    context = {
        'characters': characters,
        'characters_json': json.dumps(character_data),
    }

    return render(request, 'home/camera_simple.html', context)

def get_character_data(request):
    """
    API endpoint per ottenere i dati dei personaggi in formato JSON
    """
    if request.method == 'GET':
        characters = CharConfiguration.objects.all()
        character_data = []

        for char in characters:
            data = {
                'id': char.id,
                'name': char.name,
                'target_latitude': char.target_latitude,
                'target_longitude': char.target_longitude,
                'activation_distance': char.activation_distance,
                'character_image': char.character_image.url if char.character_image else None,
                'altitude': char.altitude,
                'height_offset': char.height_offset,
                'base_size': char.base_size,
                'facing_direction': char.facing_direction,
                'display_mode': char.display_mode,
                'use_marker': char.use_marker,
                'marker_image': char.marker_image.url if char.marker_image else None,
                'positioning_marker_image': char.positioning_marker_image.url if char.positioning_marker_image else None,
                'marker_offset_x': char.marker_offset_x,
                'marker_offset_y': char.marker_offset_y,
                'marker_offset_z': char.marker_offset_z,
                'detection_marker_features': char.detection_marker_features,
                'positioning_marker_features': char.positioning_marker_features,
            }
            character_data.append(data)

        return JsonResponse({'characters': character_data})

    return JsonResponse({'error': 'Method not allowed'}, status=405)

@staff_member_required
def marker_scanner_view(request):
    """
    Admin-only view for scanning environment and identifying good marker points
    """
    return render(request, 'home/marker_scanner.html')

@staff_member_required
@csrf_exempt
def save_marker_scan(request):
    """
    API endpoint to save scanned marker images and create character configuration
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            character_name = data.get('character_name')
            detection_marker_data = data.get('detection_marker')
            positioning_marker_data = data.get('positioning_marker')
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            altitude = data.get('altitude')
            facing_direction = data.get('facing_direction', 0)

            if not all([character_name, detection_marker_data, positioning_marker_data]):
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            # Create new character configuration
            char_config = CharConfiguration.objects.create(
                name=character_name,
                target_latitude=latitude or 0,
                target_longitude=longitude or 0,
                altitude=altitude or 0,
                activation_distance=50,
                facing_direction=facing_direction,
                use_marker=True
            )

            # Save detection marker image
            if detection_marker_data:
                format, imgstr = detection_marker_data.split(';base64,')
                ext = format.split('/')[-1]
                detection_file = ContentFile(
                    base64.b64decode(imgstr),
                    name=f'detection_marker_{char_config.id}.{ext}'
                )
                char_config.marker_image.save(
                    f'detection_marker_{char_config.id}.{ext}',
                    detection_file,
                    save=False
                )

            # Save positioning marker image
            if positioning_marker_data:
                format, imgstr = positioning_marker_data.split(';base64,')
                ext = format.split('/')[-1]
                positioning_file = ContentFile(
                    base64.b64decode(imgstr),
                    name=f'positioning_marker_{char_config.id}.{ext}'
                )
                char_config.positioning_marker_image.save(
                    f'positioning_marker_{char_config.id}.{ext}',
                    positioning_file,
                    save=False
                )

            char_config.save()

            return JsonResponse({
                'success': True,
                'character_id': char_config.id,
                'message': f'Character "{character_name}" created successfully'
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

def marker_test_view(request):
    """
    Tool per testare la qualità dei marker
    """
    return render(request, 'home/marker_test.html')

def camera_simple_gps_view(request):
    """
    View per la fotocamera AR semplificata con GPS filtering e single marker positioning
    """
    # Ottieni solo i personaggi con positioning_marker_image
    characters = CharConfiguration.objects.filter(positioning_marker_image__isnull=False).exclude(positioning_marker_image='')

    # Serializza i dati per embedding diretto nell'HTML
    character_data = []
    for char in characters:
        data = {
            'id': char.id,
            'name': char.name,
            'target_latitude': char.target_latitude,
            'target_longitude': char.target_longitude,
            'activation_distance': char.activation_distance,
            'character_image': char.character_image.url if char.character_image else None,
            'positioning_marker_image': char.positioning_marker_image.url,
            'positioning_marker_features': char.positioning_marker_features,
            'base_size': char.base_size,
            'marker_offset_x': char.marker_offset_x,
            'marker_offset_y': char.marker_offset_y,
        }
        character_data.append(data)

    context = {
        'characters': characters,
        'characters_json': json.dumps(character_data),
    }

    return render(request, 'home/camera_simple_gps.html', context)

@csrf_exempt
def yolo_detect_object(request):
    """
    API endpoint per YOLO object detection
    Riceve un frame video e rileva oggetti specifici
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        image_b64 = data.get('image')
        object_class = data.get('object_class', 'bottle')
        confidence_threshold = float(data.get('confidence_threshold', 0.5))

        if not image_b64:
            return JsonResponse({'error': 'Missing image data'}, status=400)

        # Decodifica immagine base64
        if ',' in image_b64:
            image_b64 = image_b64.split(',')[1]

        img_data = base64.b64decode(image_b64)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return JsonResponse({'error': 'Failed to decode image'}, status=400)

        # Carica modello YOLO
        model = get_yolo_model()
        if model is None:
            return JsonResponse({'error': 'YOLO model not available'}, status=500)

        # Esegui detection
        results = model(img, conf=confidence_threshold, verbose=False)

        # Estrai detections per la classe richiesta
        detections = []
        if len(results) > 0:
            result = results[0]
            boxes = result.boxes

            for box in boxes:
                cls_id = int(box.cls[0])
                class_name = result.names[cls_id]

                if class_name == object_class:
                    # Coordinate bounding box (xywh = center format)
                    x, y, w, h = box.xywh[0].tolist()
                    confidence = float(box.conf[0])

                    detections.append({
                        'class': class_name,
                        'confidence': confidence,
                        'bbox': {
                            'x': x,
                            'y': y,
                            'w': w,
                            'h': h
                        }
                    })

        return JsonResponse({
            'success': True,
            'detections': detections,
            'count': len(detections)
        })

    except Exception as e:
        import traceback
        print(f"YOLO detection error: {e}")
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)
