from rest_framework.views import APIView


class LeagueImportView(APIView):
    def get(self, request, league_code, format=None):
        raise NotImplementedError(f"Not implemented yet: you asked for {league_code}")
