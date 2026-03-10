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

    Muestra un índice de las principales funcionalidades disponibles.

    Attributes
    ----------
    template_name : str
        Ruta de la plantilla HTML utilizada para renderizar la vista.
    """

    template_name = "index.html"

    def get(self, request):
        """
        Maneja las peticiones GET mostrando la página de inicio.

        Parameters
        ----------
        request : HttpRequest
            Objeto de petición HTTP entrante.

        Returns
        -------
        HttpResponse
            Respuesta HTML con el índice de funcionalidades.
        """
        return render(request, self.template_name)


class CrearPersonajeView(View):
    """
    Controlador para la creación de nuevos personajes.

    Maneja tanto la muestra del formulario (GET) como el procesamiento
    de datos para crear un nuevo personaje (POST).

    Attributes
    ----------
    template_name : str
        Ruta de la plantilla HTML utilizada para renderizar la vista.
    form_class : PersonajeForm
        Clase del formulario asociado a la vista.
    success_url : str
        URL a la que se redirige después de una creación exitosa.
    """

    template_name = "personajes/crear.html"
    form_class = PersonajeForm
    success_url = reverse_lazy("lista_personajes")

    def get(self, request):
        """
        Maneja las peticiones GET mostrando el formulario de creación.

        Parameters
        ----------
        request : HttpRequest
            Objeto de petición HTTP entrante.

        Returns
        -------
        HttpResponse
            Respuesta HTML con el formulario renderizado.
        """
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        """
        Maneja las peticiones POST procesando los datos del formulario.

        Parameters
        ----------
        request : HttpRequest
            Objeto de petición HTTP entrante con los datos del formulario.

        Returns
        -------
        HttpResponse
            Respuesta de redirección si es válido, o el formulario con errores.
        """
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
    Controlador para mostrar el listado de todos los personajes.

    Attributes
    ----------
    template_name : str
        Ruta de la plantilla HTML utilizada para renderizar la lista.
    """

    template_name = "personajes/lista.html"

    def get(self, request):
        """
        Maneja las peticiones GET obteniendo todos los personajes.

        Parameters
        ----------
        request : HttpRequest
            Objeto de petición HTTP entrante.

        Returns
        -------
        HttpResponse
            Respuesta HTML con la lista de personajes.
        """
        personajes = service_listar()
        return render(request, self.template_name, {"personajes": personajes})


class EliminarPersonajeView(View):
    """
    Controlador para eliminar un personaje existente.

    Attributes
    ----------
    success_url : str
        URL a la que se redirige después de la eliminación.
    """

    success_url = reverse_lazy("lista_personajes")

    def post(self, request, personaje_id):
        """
        Maneja las peticiones POST eliminando el personaje especificado.

        Parameters
        ----------
        request : HttpRequest
            Objeto de petición HTTP entrante.
        personaje_id : int
            Identificador único del personaje a eliminar.

        Returns
        -------
        HttpResponse
            Respuesta de redirección a la lista de personajes.
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
    Controlador para editar un personaje existente.

    Attributes
    ----------
    template_name : str
        Ruta de la plantilla HTML utilizada para renderizar la vista.
    success_url : str
        URL a la que se redirige después de una edición exitosa.
    """

    template_name = "personajes/editar.html"
    success_url = reverse_lazy("lista_personajes")

    def get(self, request, personaje_id):
        """
        Maneja las peticiones GET mostrando el formulario de edición.

        Parameters
        ----------
        request : HttpRequest
            Objeto de petición HTTP entrante.
        personaje_id : int
            Identificador único del personaje a editar.

        Returns
        -------
        HttpResponse
            Respuesta HTML con el formulario de edición.
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
        Maneja las peticiones POST procesando los datos del formulario.

        Parameters
        ----------
        request : HttpRequest
            Objeto de petición HTTP entrante con los datos del formulario.
        personaje_id : int
            Identificador único del personaje a editar.

        Returns
        -------
        HttpResponse
            Respuesta de redirección si es válido, o el formulario con errores.
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
    template_name = "combate/index.html"

    def get(self, request):
        personajes = service_listar()
        return render(request, self.template_name, {"personajes": personajes})

    def post(self, request):
        personaje1_id = request.POST.get("personaje1")
        personaje2_id = request.POST.get("personaje2")
        guardar = request.POST.get("guardar") == "on"

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
    """Vista para entrenar un personaje (subir nivel)."""
    template_name = "personajes/entrenar.html"

    def get(self, request):
        personajes = service_listar()
        return render(request, self.template_name, {"personajes": personajes})

    def post(self, request):
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
            messages.success(request, f"{personaje.nombre} ha subido al nivel {personaje.nivel}.")
        except Exception as e:
            messages.error(request, f"Error al entrenar: {str(e)}")

        return redirect("entrenar")
