from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth.models import User
import re

from app.models import Usuario


def validar_telefono(telefono):
    """
    Valida que el teléfono tenga un formato aceptable.

    Parameters
    ----------
    telefono : str
        Número de teléfono a validar.

    Returns
    -------
    bool
        True si es válido o está vacío, False si no cumple el patrón.
    """
    if not telefono:
        return True
    patron = r"^[\d\s\+\-\(\)]{7,20}$"
    return bool(re.match(patron, telefono))


def validar_email(email):
    """
    Valida que el email tenga un formato correcto.

    Parameters
    ----------
    email : str
        Email a validar.

    Returns
    -------
    bool
        True si es válido, False si no cumple el patrón o está vacío.
    """
    if not email:
        return False
    patron = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(patron, email))


def validar_dni(dni):
    """
    Valida que el DNI tenga 8 números y 1 letra (ej: 12345678A).

    Parameters
    ----------
    dni : str
        DNI a validar.

    Returns
    -------
    bool
        True si cumple el formato, False en caso contrario.
    """
    if not dni:
        return False
    patron = r"^\d{8}[A-Z]$"
    return bool(re.match(patron, dni.upper()))


class LoginView(View):
    """Vista para iniciar sesión."""

    def get(self, request):
        """
        Renderiza la página de login si no está autenticado,
        redirige a 'home' si ya lo está.
        """
        if request.user.is_authenticated:
            return redirect("home")
        return render(request, "registration/login.html")

    def post(self, request):
        """
        Procesa el login con username y password.
        Muestra errores si los datos son incorrectos.
        """
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Redirige a 'next' si existe, sino a home
            next_url = request.GET.get("next")
            return redirect(next_url if next_url else "home")

        # Credenciales incorrectas
        messages.error(request, "Usuario o contraseña incorrectos.")
        return render(request, "registration/login.html")


class LogoutView(View):
    """Vista para cerrar sesión."""

    def get(self, request):
        logout(request)
        return redirect("login")


class RegisterView(View):
    """Vista para registrar un nuevo usuario."""

    def get(self, request):
        """Renderiza el formulario de registro si no está autenticado."""
        if request.user.is_authenticated:
            return redirect("home")
        return render(request, "registration/register.html")

    def post(self, request):
        """
        Procesa el registro de usuario y su perfil.

        Valida: contraseñas, existencia de username/DNI, formato de email/teléfono, fecha de nacimiento.
        """
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        dni = request.POST.get("dni", "").strip()
        telefono = request.POST.get("telefono", "").strip()
        email = request.POST.get("email", "").strip()
        fecha_nacimiento = request.POST.get("fecha_nacimiento") or None

        # Validaciones básicas
        if password != confirm_password:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, "registration/register.html")

        if len(password) < 8:
            messages.error(request, "La contraseña debe tener al menos 8 caracteres.")
            return render(request, "registration/register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya existe.")
            return render(request, "registration/register.html")

        if not dni:
            messages.error(request, "El DNI es obligatorio.")
            return render(request, "registration/register.html")

        if Usuario.objects.filter(DNI=dni.upper()).exists():
            messages.error(request, "El DNI ya está registrado.")
            return render(request, "registration/register.html")

        if not email:
            messages.error(request, "El email es obligatorio.")
            return render(request, "registration/register.html")

        if not fecha_nacimiento:
            messages.error(request, "La fecha de nacimiento es obligatoria.")
            return render(request, "registration/register.html")

        # Validaciones de formato
        if telefono and not validar_telefono(telefono):
            messages.error(request, "El formato del teléfono no es válido.")
            return render(request, "registration/register.html")

        if email and not validar_email(email):
            messages.error(request, "El formato del email no es válido.")
            return render(request, "registration/register.html")

        if dni and not validar_dni(dni):
            messages.error(
                request, "El DNI debe tener 8 números y 1 letra (ej: 12345678A)."
            )
            return render(request, "registration/register.html")

        # Crear el usuario y perfil
        user = User.objects.create_user(
            username=username, password=password, email=email
        )

        Usuario.objects.create(
            user=user,
            DNI=dni.upper(),
            fecha_nacimiento=fecha_nacimiento,
            telefono=telefono,
            email=email,
            monedas=10,
            mercenarios=0,
        )

        login(request, user)
        return redirect("home")
