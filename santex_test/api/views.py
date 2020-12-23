from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from api.football_data import FootballData, CompetitionNotFound


class LeagueImportView(APIView):
    def get(self, request, league_code, format=None):
        try:
            data_client = FootballData(request.query_params[FootballData.AUTH_HEADER])
            raw_competition = data_client.get_competition(league_code)
            response = Response(
                league_code,
                status=status.HTTP_501_NOT_IMPLEMENTED,
            )
        except CompetitionNotFound:
            response = Response(
                {"message": "Not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return response
