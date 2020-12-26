from django.urls import path

from api.views import LeagueImportView, PlayerCounterView

urlpatterns = [
    path("import-league/<str:league_code>", LeagueImportView.as_view()),
    path("total-players/<str:league_code>", PlayerCounterView.as_view()),
]
