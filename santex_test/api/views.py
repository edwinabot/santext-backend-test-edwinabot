from typing import List

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction


from api.football_data import FootballData, CompetitionNotFound
from api.models import Competition, Team, Player


class LeagueImportView(APIView):
    def get(self, request, league_code, format=None):
        response = Response(
            league_code,
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )

        football_data: FootballData = FootballData(
            request.query_params[FootballData.AUTH_HEADER]
        )

        try:
            raw_competition: dict = football_data.get_competition(league_code)
            competition: Competition = self.build_competition(raw_competition)
            raw_teams: List[Team] = football_data.get_competitions_teams(
                competition.code
            )
            teams = self.build_teams(raw_teams)
        except CompetitionNotFound:
            response = Response(
                {"message": "Not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        with transaction.atomic():
            competition.save()

        return response

    def build_competition(self, raw_competition):
        competition = Competition(
            name=raw_competition.get("name"),
            code=raw_competition.get("code"),
            area_name=raw_competition.get("area").get("name"),
        )
        return competition

    def build_teams(self, raw_teams):
        teams = [
            Team(name="", tla="", short_name="", area_name="", email="", competition="")
            for rt in raw_teams
        ]
        raise NotImplementedError()
