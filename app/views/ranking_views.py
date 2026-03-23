from django.shortcuts import render
from django.views import View
from app.services import ranking_usuarios, ranking_personajes
from app.views.personaje_views import get_usuario_perfil


class RankingView(View):
    """
    Controlador para la página de ranking.

    Muestra el ranking de usuarios y personajes basado en las batallas.
    Solo incluye usuarios mayores de edad.
    """

    template_name = "ranking/index.html"

    def get(self, request):
        """
        Renderiza la página de ranking con los clasificados.
        """
        perfil = get_usuario_perfil(request)
        if not perfil:
            return render(request, "registration/login.html")

        ranking_de_usuarios = ranking_usuarios()
        ranking_de_personajes = ranking_personajes()

        return render(request, self.template_name, {
            "usuarios": ranking_de_usuarios,
            "personajes": ranking_de_personajes,
        })