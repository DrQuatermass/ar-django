from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.camera_view, name='camera'),
    path('simple/', views.camera_simple_view, name='camera_simple'),
    path('simple-gps/', views.camera_simple_gps_view, name='camera_simple_gps'),
    path('api/characters/', views.get_character_data, name='character_data'),
    path('marker-scanner/', views.marker_scanner_view, name='marker_scanner'),
    path('api/save-marker-scan/', views.save_marker_scan, name='save_marker_scan'),
    path('marker-test/', views.marker_test_view, name='marker_test'),
]