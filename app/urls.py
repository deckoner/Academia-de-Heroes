from django.urls import path
from app.views import (
    HomeView,
    CrearPersonajeView,
    ListaPersonajesView,
    EliminarPersonajeView,
    EditarPersonajeView,
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('personajes/crear/', CrearPersonajeView.as_view(), name='crear_personaje'),
    path('personajes/', ListaPersonajesView.as_view(), name='lista_personajes'),
    path('personajes/<int:personaje_id>/editar/', EditarPersonajeView.as_view(), name='editar_personaje'),
    path('personajes/<int:personaje_id>/eliminar/', EliminarPersonajeView.as_view(), name='eliminar_personaje'),
]
