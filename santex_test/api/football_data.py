import requests


class FootballData:

    BASE_URL = "https://api.football-data.org/v2"
    AUTH_HEADER = "X-Auth-Token"

    def __init__(self, api_key) -> None:
        self.key = api_key

    def get_competition(self, code):
        # http://api.football-data.org/v2/competitions/PL
        try:
            url = f"{self.BASE_URL}/competitions/{code}"
            response = requests.get(
                url,
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
        try:
            url = f"{self.BASE_URL}/competitions/{code}/teams"
            response = requests.get(
                url,
                headers={
                    "content-type": "application/json",
                    self.AUTH_HEADER: self.key,
                },
            )
            response.raise_for_status()
            return response.json().get('teams')
        except requests.HTTPError:
            raise CompetitionsTeamsError(
                f"Failed to retrieve Teams for the Competition {code}"
            )

    def get_teams_players(self, cide):
        raise NotImplementedError("get_teams_players")


class CompetitionNotFound(Exception):
    pass


class CompetitionsTeamsError(Exception):
    pass
