from django.shortcuts import render
from django.views import View
from django.shortcuts import redirect
from app.services import todas_las_estadisticas
from app.views.personaje_views import get_usuario_perfil


class EstadisticasView(View):
    """
    Controlador para la pagina de estadisticas.

    Muestra graficos y datos estadisticos de la aplicacion.
    Solo accesible para el administrador (ilustre) o usuarios con es_admin=True.
    """

    template_name = "estadisticas/index.html"

    def get(self, request):
        """
        Renderiza la pagina de estadisticas si el usuario es admin.
        """
        perfil = get_usuario_perfil(request)
        if not perfil:
            return render(request, "registration/login.html")

        if perfil.user.username != "ilustre" and not perfil.es_admin:
            return redirect("home")

        estadisticas = todas_las_estadisticas()

        return render(
            request,
            self.template_name,
            {
                "estadisticas": estadisticas,
            },
        )
