from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.camera_view, name='camera'),
    path('api/characters/', views.get_character_data, name='character_data'),
]