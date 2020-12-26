from typing import List, Tuple

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction


from api.football_data import (
    FootballData,
    CompetitionNotFound,
    CompetitionsTeamsError,
    TeamError,
)
from api.models import Competition, Team, Player


class LeagueImportView(APIView):
    def get(self, request, league_code, format=None):
        try:
            if self.the_league_exists(league_code):
                response = Response(
                    {"message": "League already imported"},
                    status=status.HTTP_409_CONFLICT,
                )
                return response

            raw_competition, raw_teams, raw_players = self.extract_data(
                request, league_code
            )

            with transaction.atomic():
                self.persist_data(raw_competition, raw_teams, raw_players)

            response = Response(
                {"message": "Successfully imported"},
                status=status.HTTP_201_CREATED,
            )
        except (CompetitionNotFound, CompetitionsTeamsError, TeamError):
            response = Response(
                {"message": "Not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as ex:
            response = Response(
                {"message": "Server Error"}, status=status.HTTP_504_GATEWAY_TIMEOUT
            )

        return response

    def the_league_exists(self, code) -> bool:
        return Competition.objects.filter(code=code).exists()

    def extract_data(self, request, league_code) -> Tuple[List, List, List]:
        football_data: FootballData = FootballData(
            request.query_params[FootballData.AUTH_HEADER]
        )

        raw_competition: dict = football_data.get_competition(league_code)
        raw_teams: List[dict] = football_data.get_competitions_teams(
            raw_competition["id"]
        )
        raw_players = {
            team["tla"]: football_data.get_team_squad(team["id"]) for team in raw_teams
        }
        return raw_competition, raw_teams, raw_players

    def persist_data(self, raw_competition, raw_teams, raw_players) -> None:
        competition: Competition = self.build_competition(raw_competition)
        competition.save()
        teams = self.build_teams(raw_teams, competition)
        Team.objects.bulk_create(teams)
        teams = Team.objects.filter(competition=competition)
        players = []
        for team in teams:
            if team.tla in raw_players:
                players.extend(self.build_players(raw_players.get(team.tla), team))
        Player.objects.bulk_create(players)

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

    def build_players(self, raw_players: List[dict], team: Team):
        players = [
            Player(
                name=p.get("name"),
                position=p.get("position"),
                date_of_birth=p.get("dateOfBirth"),
                country_of_birth=p.get("countryOfBirth"),
                nationality=p.get("nationality"),
                team=team,
            )
            for p in raw_players
            if p.get("role") == "PLAYER"
        ]
        return players


"""
Additionally, expose an HTTP GET in URI /total-players/{leagueCode},
with a simple JSON response like this: {"total" : N } and HTTP Code 200.

where N is the total amount of players belonging to all teams that participate
in the given league (leagueCode). This service must rely exclusively on the data
saved inside the DB (it must not access the API football-data.org).
If the given leagueCode is not present into the DB, it should respond an HTTP Code 404.
"""


class PlayerCounterView(APIView):
    def get(self, request, league_code, format=None):
        try:
            competition = Competition.objects.get(code=league_code)
            response = Response(
                {"total": "N"},
                status=status.HTTP_200_OK,
            )
        except Competition.DoesNotExist as ex:
            response = Response(
                {"message": "Not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return response
