from django.urls import path
from django.views.generic import TemplateView
from app.views import (
    HomeView,
    CrearPersonajeView,
    ListaPersonajesView,
    EliminarPersonajeView,
    EditarPersonajeView,
    CombatirView,
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("personajes/crear/", CrearPersonajeView.as_view(), name="crear_personaje"),
    path("personajes/", ListaPersonajesView.as_view(), name="lista_personajes"),
    path(
        "personajes/<int:personaje_id>/editar/",
        EditarPersonajeView.as_view(),
        name="editar_personaje",
    ),
    path(
        "personajes/<int:personaje_id>/eliminar/",
        EliminarPersonajeView.as_view(),
        name="eliminar_personaje",
    ),
    path(
        "combate/",
        CombatirView.as_view(),
        name="combate",
    ),
    path(
        "estadisticas/",
        TemplateView.as_view(template_name="estadisticas/index.html"),
        name="estadisticas",
    ),
]
