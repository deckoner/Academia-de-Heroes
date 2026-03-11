from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from app.views import (
    HomeView,
    EnConstruccionView,
    CrearPersonajeView,
    ListaPersonajesView,
    EliminarPersonajeView,
    EditarPersonajeView,
    CombatirView,
    EntrenarPersonajeView,
)

urlpatterns = [
    path("", login_required(HomeView.as_view()), name="home"),
    path(
        "en-construccion/",
        login_required(EnConstruccionView.as_view()),
        name="en_construccion",
    ),
    path(
        "personajes/crear/",
        login_required(CrearPersonajeView.as_view()),
        name="crear_personaje",
    ),
    path(
        "personajes/",
        login_required(ListaPersonajesView.as_view()),
        name="lista_personajes",
    ),
    path(
        "personajes/<int:personaje_id>/editar/",
        login_required(EditarPersonajeView.as_view()),
        name="editar_personaje",
    ),
    path(
        "personajes/<int:personaje_id>/eliminar/",
        login_required(EliminarPersonajeView.as_view()),
        name="eliminar_personaje",
    ),
    path(
        "combate/",
        login_required(CombatirView.as_view()),
        name="combate",
    ),
    path(
        "entrenar/",
        login_required(EntrenarPersonajeView.as_view()),
        name="entrenar",
    ),
    path(
        "estadisticas/",
        login_required(TemplateView.as_view(template_name="estadisticas/index.html")),
        name="estadisticas",
    ),
]
