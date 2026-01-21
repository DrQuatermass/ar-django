from django.contrib import admin
from .models import CharConfiguration

# Register your models here.
@admin.register(CharConfiguration)
class CharacterConfigurationAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'target_latitude', 'target_longitude', 'activation_distance',
        'detection_marker_features', 'positioning_marker_features'
    ]
    readonly_fields = ['detection_marker_features', 'positioning_marker_features']

    fieldsets = (
        ('Informazioni Base', {
            'fields': ('name', 'character_image')
        }),
        ('Posizione GPS', {
            'fields': ('target_latitude', 'target_longitude', 'altitude', 'activation_distance')
        }),
        ('Configurazione 3D', {
            'fields': ('height_offset', 'base_size', 'facing_direction', 'display_mode')
        }),
        ('Marker Detection', {
            'fields': (
                'use_marker',
                'marker_image',
                'detection_marker_features',
                'positioning_marker_image',
                'positioning_marker_features',
                'marker_offset_x',
                'marker_offset_y',
                'marker_offset_z'
            ),
            'description': 'I campi "features" vengono calcolati automaticamente al caricamento delle immagini marker'
        }),
    ) 