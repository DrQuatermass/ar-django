from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class CharConfiguration(models.Model):
    DISPLAY_MODE_CHOICES = [
        ('standing', 'In piedi a terra'),
        ('floating', 'Fluttuante'),
        ('wall', 'Appeso a muro'),
    ]

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

    # Enhanced AR positioning fields
    altitude = models.FloatField(
        default=0.0,
        help_text="Altitudine in metri sul livello del mare"
    )
    height_offset = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(-10), MaxValueValidator(100)],
        help_text="Altezza dal suolo in metri (es: 1.7 per persona in piedi, 0 per oggetto a terra)"
    )
    base_size = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.1), MaxValueValidator(10)],
        help_text="Scala del personaggio (1.0 = normale, 2.0 = doppio)"
    )
    facing_direction = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(360)],
        help_text="Direzione verso cui guarda il personaggio in gradi (0=Nord, 90=Est, 180=Sud, 270=Ovest)"
    )
    display_mode = models.CharField(
        max_length=20,
        choices=DISPLAY_MODE_CHOICES,
        default='standing',
        help_text="Modalità di visualizzazione del personaggio"
    )

    # Marker-based positioning
    use_marker = models.BooleanField(
        default=False,
        help_text="Usa marker di riferimento per posizionamento preciso"
    )
    marker_image = models.ImageField(
        upload_to='markers/',
        blank=True,
        null=True,
        help_text="Immagine marker da stampare/mostrare (JPG/PNG)"
    )
    marker_offset_x = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(-10), MaxValueValidator(10)],
        help_text="Offset orizzontale dal marker in metri (positivo = destra)"
    )
    marker_offset_y = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(-10), MaxValueValidator(10)],
        help_text="Offset verticale dal marker in metri (positivo = su)"
    )
    marker_offset_z = models.FloatField(
        default=0.5,
        validators=[MinValueValidator(-10), MaxValueValidator(10)],
        help_text="Offset profondità dal marker in metri (positivo = avanti)"
    )


