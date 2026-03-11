"""
Script para crear usuarios de prueba.

Usage:
    python crear_usuarios.py
"""

import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "academia_de_heroes.settings")
sys.path.insert(0, ".")
django.setup()

from django.contrib.auth.models import User
from app.models import Usuario
from datetime import date


def crear_usuarios():
    password = "123456789"

    # gk - usuario normal mayor de edad
    user_gk = User.objects.create_user(
        username="gk", password=password, email="gk@academiaheroes.com"
    )
    Usuario.objects.create(
        user=user_gk,
        DNI="12345678A",
        fecha_nacimiento=date(1995, 5, 15),
        telefono="612345678",
        email="gk@academiaheroes.com",
        monedas=10,
    )
    print("Usuario gk creado")

    # gkChiquito - usuario menor de edad (6 años)
    user_gk_chiquito = User.objects.create_user(
        username="gkChiquito", password=password, email="gkchiquito@academiaheroes.com"
    )
    Usuario.objects.create(
        user=user_gk_chiquito,
        DNI="12345678B",
        fecha_nacimiento=date(2020, 3, 10),
        telefono="612345679",
        email="gkchiquito@academiaheroes.com",
        monedas=10,
    )
    print("Usuario gkChiquito creado (menor de edad)")

    # illustre - usuario admin
    user_ilustre = User.objects.create_user(
        username="ilustre", password=password, email="ilustre@academiaheroes.com"
    )
    Usuario.objects.create(
        user=user_ilustre,
        DNI="12345678C",
        fecha_nacimiento=date(1980, 11, 22),
        telefono="612345680",
        email="ilustre@academiaheroes.com",
        es_admin=True,
        monedas=1000,
    )
    print("Usuario illustre creado (admin)")

    print("\nTodos los usuarios creados correctamente!")
    print("Contraseña para todos: 123456789")


if __name__ == "__main__":
    # Verificar si ya existen usuarios
    if User.objects.exists():
        print("Ya existen usuarios en la base de datos. Se recrearán.")
        User.objects.all().delete()

    crear_usuarios()
