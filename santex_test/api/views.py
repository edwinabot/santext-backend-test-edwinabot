from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class LeagueImportView(APIView):
    def get(self, request, league_code, format=None):
        return Response(
            league_code,
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )
