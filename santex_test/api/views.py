from typing import List

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction


from api.football_data import FootballData, CompetitionNotFound, CompetitionsTeamsError
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

            with transaction.atomic():
                competition.save()
                teams = self.build_teams(raw_teams, competition)
                Team.objects.bulk_create(teams)
                # Player.objects.bulk_create(players)

        except (CompetitionNotFound, CompetitionsTeamsError):
            response = Response(
                {"message": "Not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return response

    def build_competition(self, raw_competition):
        competition = Competition(
            name=raw_competition.get("name"),
            code=raw_competition.get("code"),
            area_name=raw_competition.get("area").get("name"),
        )
        return competition

    def build_teams(self, raw_teams: List[dict], competition: Competition):
        teams = [
            Team(
                name=rt.get("name"),
                tla=rt.get("tla"),
                short_name=rt.get("shortName"),
                area_name=rt.get("area").get("name"),
                email=rt.get("email"),
                competition=competition,
            )
            for rt in raw_teams
        ]
        return teams
