from django.urls import path

from api.views import LeagueImportView

urlpatterns = [
    path("import-league/<str:league_code>", LeagueImportView.as_view()),
]
