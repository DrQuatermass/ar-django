from django.shortcuts import render
from django.http import JsonResponse
from .models import CharConfiguration
import json

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
        }
        character_data.append(data)

    context = {
        'characters': characters,
        'characters_json': json.dumps(character_data),  # Embedded JSON
    }

    return render(request, 'home/camera.html', context)

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
            }
            character_data.append(data)

        return JsonResponse({'characters': character_data})

    return JsonResponse({'error': 'Method not allowed'}, status=405)
