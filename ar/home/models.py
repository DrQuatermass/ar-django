from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import pre_save
from django.dispatch import receiver
import cv2
import numpy as np
from PIL import Image
import io

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
        help_text="Immagine marker per detection (decide SE mostrare il character)"
    )
    positioning_marker_image = models.ImageField(
        upload_to='markers/',
        blank=True,
        null=True,
        help_text="Immagine marker per positioning (decide DOVE posizionare il character - opzionale)"
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

    # Feature counts for dynamic thresholds
    detection_marker_features = models.IntegerField(
        default=0,
        help_text="Numero di features ORB estratti dal detection marker (calcolato automaticamente)"
    )
    positioning_marker_features = models.IntegerField(
        default=0,
        help_text="Numero di features ORB estratti dal positioning marker (calcolato automaticamente)"
    )

    # YOLO Object Detection
    use_yolo_detection = models.BooleanField(
        default=False,
        help_text="Usa YOLO per rilevare oggetti invece di marker immagine"
    )
    yolo_object_class = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Classe oggetto FISSO da rilevare nei negozi/spazi urbani. Oggetti statici consigliati: chair (sedia), couch (divano), potted plant (pianta), dining table (tavolo), bench (panchina), tv (televisore), laptop, clock (orologio), vase (vaso), book (libro), bottle (bottiglia display), wine glass (bicchiere), cup (tazza), refrigerator (frigo), microwave, oven (forno), toaster, sink (lavandino), toilet, bed (letto), desk, monitor. EVITA: person, car, bicycle e oggetti mobili."
    )
    yolo_confidence_threshold = models.FloatField(
        default=0.5,
        validators=[MinValueValidator(0.1), MaxValueValidator(1.0)],
        help_text="Soglia di confidenza minima per detection YOLO (0.5 = 50%)"
    )

    def __str__(self):
        return self.name


def extract_orb_features(image_field, nfeatures=500):
    """
    Estrae features ORB da un'immagine Django ImageField
    Returns: numero di features estratti (int)
    """
    if not image_field:
        return 0

    try:
        # Leggi l'immagine dal field
        image_field.open('rb')
        image_data = image_field.read()
        image_field.close()

        # Converti in numpy array
        pil_image = Image.open(io.BytesIO(image_data))
        img_array = np.array(pil_image.convert('RGB'))

        # Converti in grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

        # Estrai features ORB
        orb = cv2.ORB_create(nfeatures)
        keypoints, descriptors = orb.detectAndCompute(gray, None)

        return len(keypoints) if keypoints else 0
    except Exception as e:
        print(f"Error extracting ORB features: {e}")
        return 0


@receiver(pre_save, sender=CharConfiguration)
def calculate_marker_features(sender, instance, **kwargs):
    """
    Calcola automaticamente i features dei marker prima del salvataggio
    """
    # Calcola features del detection marker
    if instance.marker_image:
        try:
            # Verifica se l'immagine è cambiata
            if instance.pk:
                old_instance = CharConfiguration.objects.get(pk=instance.pk)
                if old_instance.marker_image != instance.marker_image:
                    instance.detection_marker_features = extract_orb_features(instance.marker_image, nfeatures=500)
            else:
                # Nuova istanza
                instance.detection_marker_features = extract_orb_features(instance.marker_image, nfeatures=500)
        except Exception as e:
            print(f"Error calculating detection marker features: {e}")

    # Calcola features del positioning marker
    if instance.positioning_marker_image:
        try:
            # Verifica se l'immagine è cambiata
            if instance.pk:
                old_instance = CharConfiguration.objects.get(pk=instance.pk)
                if old_instance.positioning_marker_image != instance.positioning_marker_image:
                    instance.positioning_marker_features = extract_orb_features(instance.positioning_marker_image, nfeatures=2000)
            else:
                # Nuova istanza
                instance.positioning_marker_features = extract_orb_features(instance.positioning_marker_image, nfeatures=2000)
        except Exception as e:
            print(f"Error calculating positioning marker features: {e}")


