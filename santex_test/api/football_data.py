import requests
import time


def handle_rate_limit(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.HTTPError as ex:
            if ex.request.status_code == 429:
                time.sleep(60)

    return inner


class FootballData:

    BASE_URL = "https://api.football-data.org/v2"
    AUTH_HEADER = "X-Auth-Token"

    def __init__(self, api_key) -> None:
        self.key = api_key

    @handle_rate_limit
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
            raise ex

    @handle_rate_limit
    def get_competitions_teams(self, competition_id):
        # https://api.football-data.org/v2/competitions/PL/teams
        try:
            url = f"{self.BASE_URL}/competitions/{competition_id}/teams"
            response = requests.get(
                url,
                headers={
                    "content-type": "application/json",
                    self.AUTH_HEADER: self.key,
                },
            )
            response.raise_for_status()
            return response.json().get("teams")
        except requests.HTTPError as ex:
            if ex.request.status_code != 429:
                raise CompetitionsTeamsError(
                    f"Failed to retrieve Teams for the Competition {competition_id}"
                )
            else:
                raise ex

    @handle_rate_limit
    def get_team_squad(self, team_id):
        # https://api.football-data.org/v2/teams/18
        try:
            url = f"{self.BASE_URL}/teams/{team_id}"
            response = requests.get(
                url,
                headers={
                    "content-type": "application/json",
                    self.AUTH_HEADER: self.key,
                },
            )
            response.raise_for_status()
            return response.json().get("squad")
        except requests.HTTPError as ex:
            if ex.request.status_code != 429:
                raise TeamError(f"Failed to retrieve Team {team_id}")
            else:
                raise ex


class CompetitionNotFound(Exception):
    pass


class CompetitionsTeamsError(Exception):
    pass


class TeamError(Exception):
    pass
