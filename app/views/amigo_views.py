from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from app.models import Usuario, Amigo
from app.views.personaje_views import get_usuario_perfil


class ListaAmigosView(View):
    """
    Vista para listar los amigos del usuario logueado.
    """

    template_name = "amigos/lista.html"

    def get(self, request):
        """
        Muestra la lista de amigos del usuario.
        """
        perfil = get_usuario_perfil(request)
        if not perfil:
            messages.error(request, "No tienes un perfil de usuario válido.")
            return redirect("home")

        amigos = Amigo.objects.listar_amigos(perfil)
        solicitudes_pendientes = Amigo.objects.listar_solicitudes_pendientes(perfil)
        solicitudes_enviadas = Amigo.objects.listar_solicitudes_enviadas(perfil)

        amigos_list = []
        for amigo in amigos:
            if amigo.id_usuario == perfil:
                amigos_list.append(amigo.id_amigo)
            else:
                amigos_list.append(amigo.id_usuario)

        return render(
            request,
            self.template_name,
            {
                "amigos": amigos_list,
                "solicitudes_pendientes": solicitudes_pendientes,
                "solicitudes_enviadas": solicitudes_enviadas,
            },
        )


class BuscarUsuariosView(View):
    """
    Vista para buscar usuarios y enviar solicitudes de amistad.
    """

    template_name = "amigos/buscar.html"

    def get(self, request):
        """
        Muestra el formulario de búsqueda de usuarios.
        """
        perfil = get_usuario_perfil(request)
        if not perfil:
            messages.error(request, "No tienes un perfil de usuario válido.")
            return redirect("home")

        query = request.GET.get("q", "")
        resultados = []

        if query:
            resultados = Usuario.objects.filter(
                user__username__icontains=query
            ).exclude(id=perfil.id)[:10]

        resultados_con_estado = []
        for usuario in resultados:
            estado = self.obtener_estado_amistad(perfil, usuario)
            resultados_con_estado.append({"usuario": usuario, "estado": estado})

        return render(
            request,
            self.template_name,
            {"resultados": resultados_con_estado, "query": query},
        )

    def obtener_estado_amistad(self, usuario, otro_usuario):
        """
        Obtiene el estado de la relación de amistad entre dos usuarios.

        Parameters
        ----------
        usuario : Usuario
            Usuario actual.
        otro_usuario : Usuario
            Otro usuario a verificar.

        Returns
        -------
        str
            Estado de la relación: 'amigos', 'pendiente_enviada',
            'pendiente_recibida', o None.
        """
        if Amigo.objects.son_amigos(usuario, otro_usuario):
            return "amigos"

        solicitud = Amigo.objects.tiene_solicitud_pendiente(usuario, otro_usuario)
        if solicitud:
            if solicitud.id_usuario == usuario:
                return "pendiente_enviada"
            else:
                return "pendiente_recibida"

        return None


class EnviarSolicitudView(View):
    """
    Vista para enviar una solicitud de amistad.
    """

    def post(self, request, usuario_id):
        """
        Envía una solicitud de amistad al usuario especificado.
        """
        perfil = get_usuario_perfil(request)
        if not perfil:
            messages.error(request, "No tienes un perfil de usuario válido.")
            return redirect("home")

        try:
            amigo = Usuario.objects.get(id=usuario_id)
        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no encontrado.")
            return redirect("buscar_amigos")

        if perfil.id == amigo.id:
            messages.error(request, "No puedes enviarte una solicitud a ti mismo.")
            return redirect("buscar_amigos")

        try:
            Amigo.objects.agregar_amigo(perfil, amigo)
            messages.success(request, f"Solicitud enviada a {amigo.user.username}.")
        except Exception as e:
            messages.error(request, str(e))

        return redirect("buscar_amigos")


class AceptarSolicitudView(View):
    """
    Vista para aceptar una solicitud de amistad.
    """

    def post(self, request, solicitud_id):
        """
        Acepta la solicitud de amistad especificada.
        """
        perfil = get_usuario_perfil(request)
        if not perfil:
            messages.error(request, "No tienes un perfil de usuario válido.")
            return redirect("home")

        solicitud = get_object_or_404(Amigo, id=solicitud_id, id_amigo=perfil)

        if solicitud.estado != Amigo.Estado.PENDIENTE:
            messages.error(request, "Esta solicitud ya ha sido procesada.")
            return redirect("lista_amigos")

        solicitud.estado = Amigo.Estado.ACEPTADA
        solicitud.save()

        messages.success(request, f"Aceptaste la solicitud de {solicitud.id_usuario.user.username}.")
        return redirect("lista_amigos")


class RechazarSolicitudView(View):
    """
    Vista para rechazar una solicitud de amistad.
    """

    def post(self, request, solicitud_id):
        """
        Rechaza la solicitud de amistad especificada.
        """
        perfil = get_usuario_perfil(request)
        if not perfil:
            messages.error(request, "No tienes un perfil de usuario válido.")
            return redirect("home")

        solicitud = get_object_or_404(Amigo, id=solicitud_id, id_amigo=perfil)

        if solicitud.estado != Amigo.Estado.PENDIENTE:
            messages.error(request, "Esta solicitud ya ha sido procesada.")
            return redirect("lista_amigos")

        solicitud.estado = Amigo.Estado.RECHAZADA
        solicitud.save()

        messages.success(request, f"Rechazaste la solicitud de {solicitud.id_usuario.user.username}.")
        return redirect("lista_amigos")


class EliminarAmigoView(View):
    """
    Vista para eliminar una amistad.
    """

    def post(self, request, amigo_id):
        """
        Elimina la relación de amistad especificada.
        """
        perfil = get_usuario_perfil(request)
        if not perfil:
            messages.error(request, "No tienes un perfil de usuario válido.")
            return redirect("home")

        amigo = get_object_or_404(Amigo, id=amigo_id)

        if amigo.id_usuario != perfil and amigo.id_amigo != perfil:
            messages.error(request, "No puedes eliminar esta amistad.")
            return redirect("lista_amigos")

        nombre_amigo = (
            amigo.id_amigo.user.username
            if amigo.id_usuario == perfil
            else amigo.id_usuario.user.username
        )

        amigo.delete()

        messages.success(request, f"Has eliminado a {nombre_amigo} de tus amigos.")
        return redirect("lista_amigos")
