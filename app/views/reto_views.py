from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.models import User
from app.models import Usuario, Personaje, Batalla, Amigo
from app.services.combate_service import simular_combate, guardar_resultado_combate
from app.views.personaje_views import get_usuario_perfil
import random


class RetarUsuarioView(View):
    """
    Vista para retar a un usuario.
    """

    template_name = "retos/retar.html"

    def get(self, request):
        """
        Muestra el formulario para retar a un usuario.
        """
        perfil = get_usuario_perfil(request)
        if not perfil:
            messages.error(request, "No tienes un perfil de usuario válido.")
            return redirect("home")

        amigos = self.obtener_amigos(perfil)

        username = request.GET.get("usuario", "")
        amigo_id = request.GET.get("amigo", "")
        usuario_encontrado = None
        puede_retar = False

        if amigo_id:
            try:
                amigo = Usuario.objects.get(id=amigo_id)
                usuario_encontrado = amigo
                username = amigo.user.username
                puede_retar = Personaje.objects.filter(
                    id_usuario=amigo, vivo=True
                ).exists()
            except Usuario.DoesNotExist:
                messages.error(request, "Amigo no encontrado.")
        elif username:
            try:
                user = User.objects.get(username=username)
                usuario_encontrado = Usuario.objects.get(user=user)

                if usuario_encontrado.id == perfil.id:
                    messages.error(request, "No puedes retarte a ti mismo.")
                else:
                    puede_retar = Personaje.objects.filter(
                        id_usuario=usuario_encontrado, vivo=True
                    ).exists()
            except User.DoesNotExist:
                messages.error(request, "Usuario no encontrado.")
            except Usuario.DoesNotExist:
                messages.error(request, "Usuario no encontrado.")

        personajes_atacante = Personaje.objects.filter(id_usuario=perfil, vivo=True)

        return render(
            request,
            self.template_name,
            {
                "username": username,
                "amigo_id": amigo_id,
                "amigos": amigos,
                "usuario_encontrado": usuario_encontrado,
                "puede_retar": puede_retar,
                "personajes_atacante": personajes_atacante,
            },
        )

    def obtener_amigos(self, perfil):
        """Obtiene la lista de amigos aceptados del usuario."""
        relaciones = Amigo.objects.listar_amigos(perfil)
        amigos = []
        for rel in relaciones:
            if rel.id_usuario == perfil:
                amigos.append(rel.id_amigo)
            else:
                amigos.append(rel.id_usuario)
        return amigos

    def post(self, request):
        """
        Procesa el reto: selecciona personaje del atacante,
        elige aleatoriamente del defensor y ejecuta el combate.
        """
        perfil = get_usuario_perfil(request)
        if not perfil:
            messages.error(request, "No tienes un perfil de usuario válido.")
            return redirect("home")

        username = request.POST.get("username", "")
        amigo_id = request.POST.get("amigo_id", "")
        personaje_atacante_id = request.POST.get("personaje_atacante")

        if not personaje_atacante_id:
            messages.error(request, "Faltan datos requeridos.")
            return redirect("retar_usuario")

        if amigo_id:
            try:
                defensor = Usuario.objects.get(id=amigo_id)
            except Usuario.DoesNotExist:
                messages.error(request, "Amigo no encontrado.")
                return redirect("retar_usuario")
        elif username:
            try:
                user = User.objects.get(username=username)
                defensor = Usuario.objects.get(user=user)
            except User.DoesNotExist:
                messages.error(request, "Usuario no encontrado.")
                return redirect("retar_usuario")
            except Usuario.DoesNotExist:
                messages.error(request, "Usuario no encontrado.")
                return redirect("retar_usuario")
        else:
            messages.error(
                request, "Selecciona un amigo o escribe un nombre de usuario."
            )
            return redirect("retar_usuario")

        if defensor.id == perfil.id:
            messages.error(request, "No puedes retarte a ti mismo.")
            return redirect("retar_usuario")

        try:
            personaje_atacante = Personaje.objects.get(
                id=personaje_atacante_id, id_usuario=perfil, vivo=True
            )
        except Personaje.DoesNotExist:
            messages.error(request, "Personaje del atacante no encontrado.")
            return redirect("retar_usuario")

        personajes_defensor = Personaje.objects.filter(id_usuario=defensor, vivo=True)

        if not personajes_defensor.exists():
            messages.error(
                request,
                f"El usuario {defensor.user.username} no tiene héroes vivos. Elige otro usuario.",
            )
            return redirect("retar_usuario")

        personaje_defensor = random.choice(personajes_defensor)

        resultado = simular_combate(
            personaje_atacante.id,
            personaje_defensor.id,
            usar_especial_p1=True,
            usar_especial_p2=True,
        )

        guardar_resultado_combate(
            resultado.p1["id"],
            resultado.p2["id"],
            resultado.vida1_final,
            resultado.vida2_final,
        )

        personaje_atacante.refresh_from_db()
        personaje_defensor.refresh_from_db()

        gano_atacante = resultado.ganador["id"] == resultado.p1["id"]

        if gano_atacante:
            perfil.monedas += 1
            perfil.save()

        batalla = Batalla.objects.create(
            id_atacante=perfil,
            id_defensor=defensor,
            personaje_atacante=personaje_atacante,
            personaje_defensor=personaje_defensor,
            resultado=gano_atacante,
        )

        return render(
            request,
            "combate/simulacion.html",
            {
                "resultado": resultado,
                "es_reto": True,
                "batalla": batalla,
            },
        )


class HistorialRetosView(View):
    """
    Vista para mostrar el historial de retos.
    """

    template_name = "retos/historial.html"

    def get(self, request):
        """
        Muestra el historial de retos del usuario.
        """
        perfil = get_usuario_perfil(request)
        if not perfil:
            messages.error(request, "No tienes un perfil de usuario válido.")
            return redirect("home")

        batallas = Batalla.objects.listar_por_usuario(perfil.id)

        return render(
            request,
            self.template_name,
            {"batallas": batallas},
        )
