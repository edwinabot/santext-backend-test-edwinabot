import requests
import time

from requests.exceptions import RetryError


def handle_rate_limit(func):
    """
    This decorator catches 429 errors and retries 5 times. After that it gives up
    raising an exception
    """
    def inner(*args, **kwargs):
        attempts = 0
        while attempts < 5:
            try:
                result = func(*args, **kwargs)
                return result
            except requests.HTTPError as ex:
                if ex.response.status_code == 429:
                    attempts += 1
                    time.sleep(60)
                else:
                    raise ex
        raise RetryError("Retry exceeded after being rate limited")

    return inner


class FootballData:

    BASE_URL = "https://api.football-data.org/v2"
    AUTH_HEADER = "X-Auth-Token"

    def __init__(self, api_key) -> None:
        self.key = api_key

    @handle_rate_limit
    def _make_the_request(self, url):
        response = requests.get(
            url,
            headers={
                "content-type": "application/json",
                self.AUTH_HEADER: self.key,
            },
        )
        response.raise_for_status()
        return response.json()

    def get_competition(self, code):
        # http://api.football-data.org/v2/competitions/PL
        try:
            url = f"{self.BASE_URL}/competitions/{code}"
            response = self._make_the_request(url)
            return response
        except requests.HTTPError as ex:
            if ex.response.status_code in (400, 404):
                raise CompetitionNotFound(code)
            raise ex

    def get_competitions_teams(self, competition_id):
        # https://api.football-data.org/v2/competitions/PL/teams
        try:
            url = f"{self.BASE_URL}/competitions/{competition_id}/teams"
            response = self._make_the_request(url)
            return response.get("teams")
        except requests.HTTPError as ex:
            if ex.response.status_code != 429:
                raise CompetitionsTeamsError(
                    f"Failed to retrieve Teams for the Competition {competition_id}"
                )
            else:
                raise ex

    def get_team_squad(self, team_id):
        # https://api.football-data.org/v2/teams/18
        try:
            url = f"{self.BASE_URL}/teams/{team_id}"
            response = self._make_the_request(url)
            return response.get("squad")
        except requests.HTTPError as ex:
            if ex.response.status_code != 429:
                raise TeamError(f"Failed to retrieve Team {team_id}")
            else:
                raise ex


class CompetitionNotFound(Exception):
    pass


class CompetitionsTeamsError(Exception):
    pass


class TeamError(Exception):
    pass
