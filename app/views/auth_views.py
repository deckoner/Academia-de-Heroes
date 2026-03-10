from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth.models import User

from app.models import Usuario


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

        dni = request.POST.get("dni")
        fecha_nacimiento = request.POST.get("fecha_nacimiento")
        telefono = request.POST.get("telefono")

        if password != confirm_password:

            messages.error(
                request,
                "Las contraseñas no coinciden."
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

        if dni and Usuario.objects.filter(DNI=dni).exists():

            messages.error(
                request,
                "El DNI ya está registrado."
            )

            return render(
                request,
                "registration/register.html"
            )

        user = User.objects.create_user(
            username=username,
            password=password
        )

        Usuario.objects.create(
            user=user,
            DNI=dni or "",
            fecha_nacimiento=fecha_nacimiento or None,
            telefono=telefono or "",
        )

        login(request, user)

        return redirect("home")