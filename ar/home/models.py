from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class CharConfiguration(models.Model):
    name = models.CharField(max_length=100)
    target_latitude = models.FloatField(
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        help_text="Latitudine target (-90 a 90)"
    )
    target_longitude = models.FloatField(
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        help_text="Longitudine target (-180 a 180)"
    )
    activation_distance = models.FloatField(
        default=10.0,
        validators=[MinValueValidator(1), MaxValueValidator(1000)],
        help_text="Distanza in metri per attivazione AR"
    )
    character_image = models.ImageField(
        upload_to='characters/',
        blank=True,
        null=True,
        help_text="Immagine del personaggio (PNG)"
    )


