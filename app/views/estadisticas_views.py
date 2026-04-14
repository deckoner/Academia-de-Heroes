from django.shortcuts import render
from django.views import View
from django.shortcuts import redirect
from app.services import todas_las_estadisticas
from app.views.personaje_views import get_usuario_perfil


class EstadisticasView(View):
    """
    Controlador para la página de estadísticas.

    Muestra gráficos y datos estadísticos de la aplicación.
    Solo accesible para el administrador (ilustre).
    """

    template_name = "estadisticas/index.html"

    def get(self, request):
        """
        Renderiza la página de estadísticas si el usuario es admin.
        """
        perfil = get_usuario_perfil(request)
        if not perfil:
            return render(request, "registration/login.html")

        if perfil.user.username != "ilustre":
            return redirect("home")

        estadisticas = todas_las_estadisticas()

        return render(request, self.template_name, {
            "estadisticas": estadisticas,
        })
