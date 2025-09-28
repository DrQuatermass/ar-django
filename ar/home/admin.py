from django.contrib import admin
from .models import CharConfiguration

# Register your models here.
@admin.register(CharConfiguration)
class CharacterConfigurationAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'target_latitude', 'target_longitude', 'activation_distance'
    ] 