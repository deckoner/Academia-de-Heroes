from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth.models import User
import re

from app.models import Usuario


def validar_telefono(telefono):
    """Valida que el teléfono tenga un formato válido."""
    if not telefono:
        return True
    patron = r'^[\d\s\+\-\(\)]{7,20}$'
    return bool(re.match(patron, telefono))


def validar_email(email):
    """Valida que el email tenga un formato válido."""
    if not email:
        return True
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(patron, email))


def validar_dni(dni):
    """Valida que el DNI tenga un formato válido (8 números + 1 letra)."""
    if not dni:
        return True
    patron = r'^\d{8}[A-Z]$'
    return bool(re.match(patron, dni.upper()))


class LoginView(View):

    def get(self, request):

        if request.user.is_authenticated:
            return redirect("home")

        return render(request, "registration/login.html")

    def post(self, request):

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            next_url = request.GET.get("next")

            return redirect(
                next_url if next_url else "home"
            )

        messages.error(request, "Usuario o contraseña incorrectos.")

        return render(request, "registration/login.html")


class LogoutView(View):

    def get(self, request):

        logout(request)

        return redirect("login")


class RegisterView(View):

    def get(self, request):

        if request.user.is_authenticated:
            return redirect("home")

        return render(
            request,
            "registration/register.html"
        )

    def post(self, request):

        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        dni = request.POST.get("dni", "").strip()
        telefono = request.POST.get("telefono", "").strip()
        email = request.POST.get("email", "").strip()
        fecha_nacimiento = request.POST.get("fecha_nacimiento") or None

        if password != confirm_password:

            messages.error(
                request,
                "Las contraseñas no coinciden."
            )

            return render(
                request,
                "registration/register.html"
            )

        if len(password) < 8:

            messages.error(
                request,
                "La contraseña debe tener al menos 8 caracteres."
            )

            return render(
                request,
                "registration/register.html"
            )

        if User.objects.filter(username=username).exists():

            messages.error(
                request,
                "El nombre de usuario ya existe."
            )

            return render(
                request,
                "registration/register.html"
            )

        if dni and Usuario.objects.filter(DNI=dni.upper()).exists():

            messages.error(
                request,
                "El DNI ya está registrado."
            )

            return render(
                request,
                "registration/register.html"
            )

        if telefono and not validar_telefono(telefono):

            messages.error(
                request,
                "El formato del teléfono no es válido."
            )

            return render(
                request,
                "registration/register.html"
            )

        if email and not validar_email(email):

            messages.error(
                request,
                "El formato del email no es válido."
            )

            return render(
                request,
                "registration/register.html"
            )

        if dni and not validar_dni(dni):

            messages.error(
                request,
                "El DNI debe tener 8 números y 1 letra (ej: 12345678A)."
            )

            return render(
                request,
                "registration/register.html"
            )

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email if email else ""
        )

        Usuario.objects.create(
            user=user,
            DNI=dni.upper() if dni else "",
            fecha_nacimiento=fecha_nacimiento,
            telefono=telefono,
            email=email
        )

        login(request, user)

        return redirect("home")
