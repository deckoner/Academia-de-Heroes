from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.urls import reverse_lazy
from app.forms.personaje_form import PersonajeForm
from app.services import (
    listar_personajes as service_listar,
    obtener_personaje as service_obtener,
    borrar_personaje as service_borrar,
)
from app.services.combate_service import simular_combate
from app.models import Usuario, Personaje, Batalla, Amigo


def get_usuario_perfil(request):
    """
    Obtiene el perfil de usuario logueado.

    Args:
        request: Objeto HttpRequest con la sesión del usuario.

    Returns:
        Objeto Usuario si existe el perfil, None en caso contrario.
    """
    if not request.user.is_authenticated:
        return None
    try:
        return request.user.perfil
    except Usuario.DoesNotExist:
        return None


class HomeView(View):
    """
    Controlador para la página de inicio.

    Muestra un índice de funcionalidades principales.
    """

    template_name = "index.html"

    def get(self, request):
        """
        Renderiza la página de inicio.
        """
        perfil = get_usuario_perfil(request)
        if not perfil:
            return redirect("login")

        batallas = Batalla.objects.listar_por_usuario(perfil.id)[:10]
        
        solicitudes_pendientes = Amigo.objects.listar_solicitudes_pendientes(perfil)
        
        batallas_pendientes = Batalla.objects.filter(
            id_defensor=perfil, leido=False
        )

        return render(request, self.template_name, {
            "batallas": batallas,
            "solicitudes_pendientes": solicitudes_pendientes,
            "batallas_pendientes": batallas_pendientes,
            "usuario_id": perfil.id,
        })

    def post(self, request):
        """
        Maneja marcar batallas como leídas.
        """
        perfil = get_usuario_perfil(request)
        if not perfil:
            return redirect("login")

        batalla_id = request.POST.get("batalla_id")
        if batalla_id:
            try:
                batalla = Batalla.objects.get(id=batalla_id, id_defensor=perfil)
                batalla.leido = True
                batalla.save()
                messages.success(request, "Batalla marcada como leída.")
            except Batalla.DoesNotExist:
                messages.error(request, "Batalla no encontrada.")

        return redirect("home")


class EnConstruccionView(View):
    """
    Controlador para páginas en construcción.

    Muestra un mensaje indicando que la funcionalidad
    está actualmente en desarrollo.
    """

    template_name = "en_construccion.html"

    def get(self, request):
        """
        Renderiza la página de construcción.
        """
        return render(request, self.template_name)


class CrearPersonajeView(View):
    """
    Vista para crear un nuevo personaje.

    Gestiona tanto la visualización del formulario como el procesamiento
    de los datos enviados. El personaje se asocia automáticamente
    al usuario logueado.
    """

    template_name = "personajes/crear.html"
    form_class = PersonajeForm
    success_url = reverse_lazy("lista_personajes")

    def get(self, request):
        """Muestra el formulario vacío para crear un personaje."""
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        """
        Procesa los datos del formulario y crea el personaje.

        El personaje se asocia automáticamente al usuario logueado.
        """
        form = self.form_class(request.POST)

        if form.is_valid():
            try:
                perfil = get_usuario_perfil(request)
                if not perfil:
                    messages.error(request, "No tienes un perfil de usuario válido.")
                    return render(request, self.template_name, {"form": form})

                personaje = form.save(commit=False)
                personaje.id_usuario = perfil
                personaje.save()

                messages.success(
                    request,
                    f'Personaje "{form.cleaned_data["nombre"]}" creado correctamente.',
                )
                return redirect(self.success_url)
            except Exception as e:
                messages.error(request, f"Error al crear el personaje: {str(e)}")

        return render(request, self.template_name, {"form": form})


class ListaPersonajesView(View):
    """
    Vista para listar los personajes del usuario logueado.

    Muestra únicamente los personajes del usuario actual.
    """

    template_name = "personajes/lista.html"

    def get(self, request):
        """
        Obtiene los personajes del usuario logueado y los envía a la plantilla.

        Returns:
            HttpResponse con la lista de personajes del usuario.
        """
        perfil = get_usuario_perfil(request)
        if not perfil:
            messages.error(request, "No tienes un perfil de usuario válido.")
            return redirect("home")

        personajes = Personaje.objects.filter(id_usuario=perfil)
        return render(request, self.template_name, {"personajes": personajes})


class EliminarPersonajeView(View):
    """
    Vista para eliminar un personaje existente.

    Verifica que el personaje pertenece al usuario logueado
    antes de eliminarlo.
    """

    success_url = reverse_lazy("lista_personajes")

    def post(self, request, personaje_id):
        """
        Elimina un personaje dado su ID.

        Solo permite eliminar personajes propios.
        Muestra mensajes de éxito o error según corresponda.
        """
        perfil = get_usuario_perfil(request)
        if not perfil:
            messages.error(request, "No tienes un perfil de usuario válido.")
            return redirect(self.success_url)

        personaje = service_obtener(personaje_id)

        if not personaje:
            messages.error(request, "Personaje no encontrado.")
            return redirect(self.success_url)

        if personaje.id_usuario != perfil:
            messages.error(request, "No puedes eliminar personajes de otros usuarios.")
            return redirect(self.success_url)

        try:
            nombre = personaje.nombre
            service_borrar(personaje_id)
            messages.success(request, f'Personaje "{nombre}" eliminado correctamente.')
        except Exception as e:
            messages.error(request, f"Error al eliminar el personaje: {str(e)}")

        return redirect(self.success_url)


class EditarPersonajeView(View):
    """
    Vista para editar un personaje existente.

    Permite mostrar el formulario con los datos actuales y actualizarlo.
    Solo permite editar personajes propios.
    """

    template_name = "personajes/editar.html"
    success_url = reverse_lazy("lista_personajes")

    def get(self, request, personaje_id):
        """
        Muestra el formulario de edición con los datos actuales del personaje.

        Solo permite editar personajes propios.
        """
        perfil = get_usuario_perfil(request)
        if not perfil:
            messages.error(request, "No tienes un perfil de usuario válido.")
            return redirect(self.success_url)

        personaje = service_obtener(personaje_id)

        if not personaje:
            messages.error(request, "Personaje no encontrado.")
            return redirect(self.success_url)

        if personaje.id_usuario != perfil:
            messages.error(request, "No puedes editar personajes de otros usuarios.")
            return redirect(self.success_url)

        initial_data = {
            "tipo": personaje.tipo,
            "nombre": personaje.nombre,
            "nivel": personaje.nivel,
            "vida": personaje.vida,
            "vida_max": personaje.vida_max,
            "armadura": personaje.armadura,
            "mana": personaje.mana,
            "precision": personaje.precision,
        }

        form = PersonajeForm(initial=initial_data, instance=personaje)
        return render(
            request, self.template_name, {"form": form, "personaje": personaje}
        )

    def post(self, request, personaje_id):
        """
        Procesa los datos del formulario y actualiza el personaje.

        Solo permite actualizar personajes propios.
        """
        perfil = get_usuario_perfil(request)
        if not perfil:
            messages.error(request, "No tienes un perfil de usuario válido.")
            return redirect(self.success_url)

        personaje = service_obtener(personaje_id)

        if not personaje:
            messages.error(request, "Personaje no encontrado.")
            return redirect(self.success_url)

        if personaje.id_usuario != perfil:
            messages.error(request, "No puedes editar personajes de otros usuarios.")
            return redirect(self.success_url)

        form = PersonajeForm(request.POST, instance=personaje)

        if form.is_valid():
            try:
                form.save()
                messages.success(
                    request,
                    f'Personaje "{form.cleaned_data["nombre"]}" actualizado correctamente.',
                )
                return redirect(self.success_url)
            except Exception as e:
                messages.error(request, f"Error al actualizar el personaje: {str(e)}")

        return render(
            request, self.template_name, {"form": form, "personaje": personaje}
        )


class CombatirView(View):
    """
    Vista para gestionar combates entre personajes.

    Permite seleccionar dos personajes del mismo usuario y simular el combate.
    Los combates son simulaciones y no se guardan en el servidor.
    """

    template_name = "combate/index.html"

    def get(self, request):
        """
        Muestra el formulario de combate con los personajes del usuario.

        Returns:
            HttpResponse con el formulario de combate.
        """
        perfil = get_usuario_perfil(request)
        if not perfil:
            messages.error(request, "No tienes un perfil de usuario válido.")
            return redirect("home")

        personajes = Personaje.objects.filter(id_usuario=perfil)
        return render(request, self.template_name, {"personajes": personajes})

    def post(self, request):
        """
        Procesa la selección de personajes y simula el combate.

        Los combates son simulaciones y no se guardan en la base de datos.
        No se otorgan monedas por ganar.
        """
        perfil = get_usuario_perfil(request)
        if not perfil:
            messages.error(request, "No tienes un perfil de usuario válido.")
            return redirect("home")

        personaje1_id = request.POST.get("personaje1")
        personaje2_id = request.POST.get("personaje2")

        if not personaje1_id or not personaje2_id:
            messages.error(request, "Selecciona dos personajes para el combate.")
            return redirect("combate")

        try:
            personaje1_id = int(personaje1_id)
            personaje2_id = int(personaje2_id)
        except ValueError:
            messages.error(request, "IDs inválidos.")
            return redirect("combate")

        personaje1 = service_obtener(personaje1_id)
        personaje2 = service_obtener(personaje2_id)

        if not personaje1 or not personaje2:
            messages.error(request, "Personaje no encontrado.")
            return redirect("combate")

        if personaje1.id_usuario != perfil or personaje2.id_usuario != perfil:
            messages.error(request, "Solo puedes combatir con tus propios personajes.")
            return redirect("combate")

        if service_listar().count() < 2:
            messages.error(request, "Se necesitan al menos dos personajes.")
            return redirect("combate")

        if personaje1_id == personaje2_id:
            messages.error(
                request, "No puedes enfrentar a un personaje contra si mismo."
            )
            return redirect("combate")

        try:
            resultado = simular_combate(personaje1_id, personaje2_id)
            return render(request, "combate/simulacion.html", {"resultado": resultado})
        except ValueError as e:
            messages.error(request, str(e))
            return redirect("combate")


class EntrenarPersonajeView(View):
    """
    Vista para entrenar un personaje y subirlo de nivel.

    Solo permite entrenar personajes propios utilizando mercenarios.
    Los mercenarios se pueden comprar con oro.
    """

    template_name = "personajes/entrenar.html"
    COSTO_MERCENARIO = 1

    def get(self, request):
        """
        Muestra la lista de personajes disponibles para entrenamiento.

        Returns:
            HttpResponse con la lista de personajes del usuario y su información de mercenarios.
        """
        perfil = get_usuario_perfil(request)
        if not perfil:
            messages.error(request, "No tienes un perfil de usuario válido.")
            return redirect("home")

        personajes = Personaje.objects.filter(id_usuario=perfil)
        return render(
            request,
            self.template_name,
            {
                "personajes": personajes,
                "monedas": perfil.monedas,
                "mercenarios": perfil.mercenarios,
                "costo_mercanario": self.COSTO_MERCENARIO,
            },
        )

    def post(self, request):
        """
        Procesa el entrenamiento de un personaje seleccionado.

        Utiliza mercenarios para subir el nivel del personaje.
        """
        perfil = get_usuario_perfil(request)
        if not perfil:
            messages.error(request, "No tienes un perfil de usuario válido.")
            return redirect("entrenar")

        accion = request.POST.get("accion")

        if accion == "comprar":
            return self.comprar_mercanario(request, perfil)

        return self.entrenar_personaje(request, perfil)

    def comprar_mercanario(self, request, perfil):
        """
        Compra un mercenario usando monedas de oro.

        Args:
            request: Objeto HttpRequest con los datos de la petición.
            perfil: Objeto Usuario con el perfil del usuario.

        Returns:
            Redirección a la página de entrenar.
        """
        if perfil.monedas < self.COSTO_MERCENARIO:
            messages.error(request, "No tienes suficientes monedas.")
            return redirect("entrenar")

        try:
            perfil.monedas -= self.COSTO_MERCENARIO
            perfil.mercenarios += 1
            perfil.save()
            messages.success(request, "¡Mercenario contratado correctamente!")
        except Exception as e:
            messages.error(request, f"Error al comprar mercenario: {str(e)}")

        return redirect("entrenar")

    def entrenar_personaje(self, request, perfil):
        """
        Entrena un personaje usando un mercenario.

        Args:
            request: Objeto HttpRequest con los datos de la petición.
            perfil: Objeto Usuario con el perfil del usuario.

        Returns:
            Redirección a la página de entrenar.
        """
        personaje_id = request.POST.get("personaje_id")

        if not personaje_id:
            messages.error(request, "Selecciona un personaje para entrenar.")
            return redirect("entrenar")

        try:
            personaje_id = int(personaje_id)
        except ValueError:
            messages.error(request, "ID inválido.")
            return redirect("entrenar")

        personaje = service_obtener(personaje_id)

        if not personaje:
            messages.error(request, "Personaje no encontrado.")
            return redirect("entrenar")

        if personaje.id_usuario != perfil:
            messages.error(request, "No puedes entrenar personajes de otros usuarios.")
            return redirect("entrenar")

        if perfil.mercenarios < 1:
            messages.error(request, "No tienes mercenarios suficientes. ¡Compra uno!")
            return redirect("entrenar")

        try:
            perfil.mercenarios -= 1
            perfil.save()

            personaje.subir_nivel()
            personaje.save()

            messages.success(
                request, f"{personaje.nombre} ha subido al nivel {personaje.nivel}."
            )
        except Exception as e:
            messages.error(request, f"Error al entrenar: {str(e)}")

        return redirect("entrenar")
