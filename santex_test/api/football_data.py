import requests


class FootballData:

    BASE_URL = "https://api.football-data.org/v2"
    AUTH_HEADER = "X-Auth-Token"

    def __init__(self, api_key) -> None:
        self.key = api_key

    def get_competition(self, code):
        # http://api.football-data.org/v2/competitions/PL
        try:
            response = requests.get(
                f"{self.BASE_URL}/competitions/{code}",
                headers={
                    "content-type": "application/json",
                    self.AUTH_HEADER: self.key,
                },
            )
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as ex:
            if ex.response.status_code in (400, 404):
                raise CompetitionNotFound(code)

    def get_competitions_teams(self, code):
        # https://api.football-data.org/v2/competitions/PL/teams
        raise NotImplementedError("get_competitions_teams")

    def get_teams_players(self, cide):
        raise NotImplementedError("get_teams_players")


class CompetitionNotFound(Exception):
    pass