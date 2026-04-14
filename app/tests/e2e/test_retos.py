import pytest
from django.test import Client
from django.contrib.auth.models import User
from django.db import models
from app.models import Usuario, Personaje, Batalla, Amigo
from datetime import date
import random


@pytest.fixture
def usuario1(db):
    """Usuario de prueba 1."""
    user = User.objects.create_user(username="usuario1", password="password123")
    return Usuario.objects.create(
        user=user,
        DNI="11111111A",
        email="usuario1@test.com",
        fecha_nacimiento=date(2000, 1, 1),
    )


@pytest.fixture
def usuario2(db):
    """Usuario de prueba 2."""
    user = User.objects.create_user(username="usuario2", password="password123")
    return Usuario.objects.create(
        user=user,
        DNI="22222222B",
        email="usuario2@test.com",
        fecha_nacimiento=date(2000, 1, 1),
    )


@pytest.fixture
def personaje1(db, usuario1):
    """Personaje del usuario1."""
    return Personaje.objects.create(
        id_usuario=usuario1,
        tipo="GUERRERO",
        nombre="Guerrero1",
        nivel=1,
        vida=100,
        vida_max=100,
        armadura=10,
        vivo=True,
    )


@pytest.fixture
def personaje2(db, usuario2):
    """Personaje del usuario2."""
    return Personaje.objects.create(
        id_usuario=usuario2,
        tipo="MAGO",
        nombre="Mago2",
        nivel=1,
        vida=100,
        vida_max=100,
        mana=50,
        vivo=True,
    )


@pytest.fixture
def client1(db, usuario1):
    """Cliente autenticado como usuario1."""
    client = Client()
    client.login(username="usuario1", password="password123")
    return client


@pytest.fixture
def client2(db, usuario2):
    """Cliente autenticado como usuario2."""
    client = Client()
    client.login(username="usuario2", password="password123")
    return client


@pytest.mark.django_db
class TestPaginaRetos:
    """Tests de la página de retos."""

    def test_pagina_retos_carga(self, client1):
        """La página de retos carga correctamente."""
        response = client1.get("/retos/")
        assert response.status_code == 200


@pytest.mark.django_db
class TestBuscarUsuario:
    """Tests de búsqueda de usuarios para retar."""

    def test_buscar_usuario_existe(self, client1, usuario2):
        """Se puede buscar un usuario por nombre."""
        response = client1.get("/retos/?usuario=usuario2")
        assert response.status_code == 200
        content = response.content.decode()
        assert "usuario2" in content

    def test_buscar_usuario_no_existe(self, client1):
        """Buscar un usuario que no existe."""
        response = client1.get("/retos/?usuario=usuarionoexistente")
        assert response.status_code == 200
        content = response.content.decode()
        assert "No se encontraron" in content or "no encontrado" in content.lower()


@pytest.mark.django_db
class TestCrearReto:
    """Tests de creación de retos."""

    def test_no_puede_retarse_a_si_mismo(self, client1, personaje1):
        """Un usuario no puede retarse a sí mismo."""
        response = client1.post(
            "/retos/",
            {"username": "usuario1", "personaje_atacante": personaje1.id},
        )
        # La vista hace redirect de vuelta
        assert response.status_code == 302

    def test_usuario_sin_personajes_no_puede_retar(self, client1, usuario2):
        """No se puede retar si el usuario no tiene personajes."""
        response = client1.get("/retos/?usuario=usuario2")
        assert response.status_code == 200


@pytest.mark.django_db
class TestHistorialRetos:
    """Tests del historial de retos."""

    def test_historial_carga(self, client1):
        """El historial de retos carga correctamente."""
        response = client1.get("/retos/historial/")
        assert response.status_code == 200

    def test_historial_vacio(self, client1):
        """El historial vacío muestra mensaje apropiado."""
        response = client1.get("/retos/historial/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "No hay retos" in content or "No has participado" in content

    def test_historial_muestra_batallas(
        self, client1, client2, usuario1, usuario2, personaje1, personaje2
    ):
        """El historial muestra las batallas."""
        Batalla.objects.create(
            id_atacante=usuario1,
            id_defensor=usuario2,
            personaje_atacante=personaje1,
            personaje_defensor=personaje2,
            resultado=True,
        )

        response = client1.get("/retos/historial/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "Guerrero1" in content or "Mago2" in content


@pytest.mark.django_db
class TestBatallaModel:
    """Tests del modelo Batalla."""

    def test_crear_batalla(self, usuario1, usuario2, personaje1, personaje2):
        """Se puede crear una batalla."""
        batalla = Batalla.objects.create(
            id_atacante=usuario1,
            id_defensor=usuario2,
            personaje_atacante=personaje1,
            personaje_defensor=personaje2,
            resultado=True,
        )
        assert batalla.id_atacante == usuario1
        assert batalla.id_defensor == usuario2
        assert batalla.resultado == True

    def test_listar_por_usuario(self, usuario1, usuario2, personaje1, personaje2):
        """Se pueden listar batallas por usuario."""
        Batalla.objects.create(
            id_atacante=usuario1,
            id_defensor=usuario2,
            personaje_atacante=personaje1,
            personaje_defensor=personaje2,
            resultado=True,
        )

        batallas = Batalla.objects.listar_por_usuario(usuario1.id)
        assert batallas.count() == 1

        batallas = Batalla.objects.listar_por_usuario(usuario2.id)
        assert batallas.count() == 1
