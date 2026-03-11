from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.urls import reverse_lazy
from app.forms.personaje_form import PersonajeForm
from app.services import (
    crear_personaje as service_crear,
    listar_personajes as service_listar,
    obtener_personaje as service_obtener,
    borrar_personaje as service_borrar,
    actualizar_personaje as service_actualizar,
)
from app.services.combate_service import simular_combate, guardar_resultado_combate


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
        return render(request, self.template_name)


class CrearPersonajeView(View):
    """
    Vista para crear un nuevo personaje.

    Gestiona tanto la visualización del formulario como el procesamiento
    de los datos enviados.
    """

    template_name = "personajes/crear.html"
    form_class = PersonajeForm
    success_url = reverse_lazy("lista_personajes")

    def get(self, request):
        """Muestra el formulario vacío para crear un personaje."""
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        """Procesa los datos del formulario y crea el personaje."""
        form = self.form_class(request.POST)

        if form.is_valid():
            try:
                form.save()
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
    Vista para listar todos los personajes disponibles.
    """

    template_name = "personajes/lista.html"

    def get(self, request):
        """
        Obtiene todos los personajes y los envía a la plantilla.
        """
        personajes = service_listar()
        return render(request, self.template_name, {"personajes": personajes})


class EliminarPersonajeView(View):
    """
    Vista para eliminar un personaje existente.
    """

    success_url = reverse_lazy("lista_personajes")

    def post(self, request, personaje_id):
        """
        Elimina un personaje dado su ID.

        Muestra mensajes de éxito o error según corresponda.
        """
        personaje = service_obtener(personaje_id)

        if not personaje:
            messages.error(request, "Personaje no encontrado.")
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
    """

    template_name = "personajes/editar.html"
    success_url = reverse_lazy("lista_personajes")

    def get(self, request, personaje_id):
        """
        Muestra el formulario de edición con los datos actuales del personaje.
        """
        personaje = service_obtener(personaje_id)

        if not personaje:
            messages.error(request, "Personaje no encontrado.")
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
        """
        personaje = service_obtener(personaje_id)

        if not personaje:
            messages.error(request, "Personaje no encontrado.")
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

    Permite seleccionar dos personajes y simular el combate.
    """

    template_name = "combate/index.html"

    def get(self, request):
        """Muestra el formulario de combate con todos los personajes."""
        personajes = service_listar()
        return render(request, self.template_name, {"personajes": personajes})

    def post(self, request):
        """
        Procesa la selección de personajes y simula el combate.
        Guarda los resultados si el usuario lo indica.
        """
        personaje1_id = request.POST.get("personaje1")
        personaje2_id = request.POST.get("personaje2")
        guardar = request.POST.get("guardar") == "on"

        # Validaciones básicas
        if not personaje1_id or not personaje2_id:
            messages.error(request, "Selecciona dos personajes para el combate.")
            return redirect("combate")

        try:
            personaje1_id = int(personaje1_id)
            personaje2_id = int(personaje2_id)
        except ValueError:
            messages.error(request, "IDs inválidos.")
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

            if guardar:
                guardar_resultado_combate(
                    personaje1_id,
                    personaje2_id,
                    resultado.vida1_final,
                    resultado.vida2_final,
                )

            return render(request, "combate/simulacion.html", {"resultado": resultado})
        except ValueError as e:
            messages.error(request, str(e))
            return redirect("combate")


class EntrenarPersonajeView(View):
    """
    Vista para entrenar un personaje y subirlo de nivel.
    """

    template_name = "personajes/entrenar.html"

    def get(self, request):
        """Muestra la lista de personajes disponibles para entrenamiento."""
        personajes = service_listar()
        return render(request, self.template_name, {"personajes": personajes})

    def post(self, request):
        """
        Procesa el entrenamiento de un personaje seleccionado.
        Incrementa su nivel y guarda los cambios.
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

        try:
            personaje.subir_nivel()
            personaje.save()
            messages.success(
                request, f"{personaje.nombre} ha subido al nivel {personaje.nivel}."
            )
        except Exception as e:
            messages.error(request, f"Error al entrenar: {str(e)}")

        return redirect("entrenar")
