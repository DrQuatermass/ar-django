from django.core.management.base import BaseCommand
from home.models import CharConfiguration, extract_orb_features


class Command(BaseCommand):
    help = 'Ricalcola i features ORB per tutti i marker esistenti'

    def handle(self, *args, **options):
        characters = CharConfiguration.objects.all()
        updated_count = 0

        for char in characters:
            updated = False

            # Calcola features detection marker
            if char.marker_image:
                try:
                    features = extract_orb_features(char.marker_image, nfeatures=500)
                    char.detection_marker_features = features
                    updated = True
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'OK {char.name}: Detection marker = {features} features'
                        )
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'ERR {char.name}: Errore detection marker - {str(e)}'
                        )
                    )

            # Calcola features positioning marker
            if char.positioning_marker_image:
                try:
                    features = extract_orb_features(char.positioning_marker_image, nfeatures=2000)
                    char.positioning_marker_features = features
                    updated = True
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'OK {char.name}: Positioning marker = {features} features'
                        )
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'ERR {char.name}: Errore positioning marker - {str(e)}'
                        )
                    )

            if updated:
                char.save()
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'\nOK Completato! {updated_count} characters aggiornati.'
            )
        )
