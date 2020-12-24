from typing import List

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
        football_data: FootballData = FootballData(
            request.query_params[FootballData.AUTH_HEADER]
        )

        try:
            raw_competition: dict = football_data.get_competition(league_code)
            raw_teams: List[dict] = football_data.get_competitions_teams(
                raw_competition["id"]
            )
            raw_players = {
                team["tla"]: football_data.get_team_squad(team["id"])
                for team in raw_teams[:2]
            }

            with transaction.atomic():
                competition: Competition = self.build_competition(raw_competition)
                competition.save()
                teams = self.build_teams(raw_teams, competition)
                Team.objects.bulk_create(teams)
                players = []
                for team in teams:
                    players += self.build_players(raw_players.get(team.tla), team)
                Player.objects.bulk_create(players)

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
            print(ex)
            response = Response(
                ex,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
        ]
        return players
