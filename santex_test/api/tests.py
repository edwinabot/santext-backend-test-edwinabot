# https://pytest-django.readthedocs.io/en/latest/helpers.html#id2
import os

import pytest
import requests_mock

from requests.exceptions import ConnectionError
from django.db import Error as DBError

from api.views import LeagueImportView
from api.football_data import FootballData


@pytest.mark.not_mocked
def test_import_league_201(client, db):
    """
    HttpCode 201, {"message": "Successfully imported"} -->
        When the leagueCode was successfully imported.
    """
    response = client.get(
        "/api/import-league/ELC", {"X-Auth-Token": os.getenv("API_KEY", "NOTOKEN")}
    )
    assert response.status_code == 201
    assert response.json()["message"] == "Successfully imported"


def import_mock_league(client):
    # MOCK Prep
    mock_competition = {
        "id": 2016,
        "area": {"id": 2072, "name": "England"},
        "name": "Championship",
        "code": "ELC",
        "emblemUrl": None,
        "plan": "TIER_ONE",
        "currentSeason": {
            "id": 628,
            "startDate": "2020-09-12",
            "endDate": "2021-08-04",
            "currentMatchday": 21,
            "winner": None,
        },
        "seasons": [],
        "lastUpdated": "2020-12-19T18:59:48Z",
    }

    mock_competition_teams = {
        "count": 24,
        "filters": {},
        "competition": {
            "id": 2016,
            "area": {"id": 2072, "name": "England"},
            "name": "Championship",
            "code": "ELC",
            "plan": "TIER_ONE",
            "lastUpdated": "2020-12-19T18:59:48Z",
        },
        "season": {
            "id": 628,
            "startDate": "2020-09-12",
            "endDate": "2021-08-04",
            "currentMatchday": 21,
            "winner": None,
        },
        "teams": [
            {
                "id": 59,
                "area": {"id": 2072, "name": "England"},
                "name": "Blackburn Rovers FC",
                "shortName": "Blackburn",
                "tla": "BBR",
                "crestUrl": "https://crests.football-data.org/59.svg",
                "address": "Ewood Park Blackburn BB2 4JF",
                "phone": "+44 (0871) 7021875",
                "website": "http://www.rovers.co.uk",
                "email": None,
                "founded": 1874,
                "clubColors": "Blue / White",
                "venue": "Ewood Park",
                "lastUpdated": "2020-11-26T02:16:34Z",
            },
        ],
    }

    mock_teams = {
        "id": 59,
        "area": {"id": 2072, "name": "England"},
        "activeCompetitions": [
            {
                "id": 2139,
                "area": {"id": 2072, "name": "England"},
                "name": "Football League Cup",
                "code": "FLC",
                "plan": "TIER_THREE",
                "lastUpdated": "2020-12-24T01:45:03Z",
            },
            {
                "id": 2016,
                "area": {"id": 2072, "name": "England"},
                "name": "Championship",
                "code": "ELC",
                "plan": "TIER_ONE",
                "lastUpdated": "2020-12-19T18:59:48Z",
            },
        ],
        "name": "Blackburn Rovers FC",
        "shortName": "Blackburn",
        "tla": "BBR",
        "crestUrl": "https://crests.football-data.org/59.svg",
        "address": "Ewood Park Blackburn BB2 4JF",
        "phone": "+44 (0871) 7021875",
        "website": "http://www.rovers.co.uk",
        "email": None,
        "founded": 1874,
        "clubColors": "Blue / White",
        "venue": "Ewood Park",
        "squad": [
            {
                "id": 3996,
                "name": "Tom Trybull",
                "position": "Midfielder",
                "dateOfBirth": "1993-03-09T00:00:00Z",
                "countryOfBirth": "Germany",
                "nationality": "Germany",
                "shirtNumber": None,
                "role": "PLAYER",
            },
            {
                "id": 4085,
                "name": "Barry Douglas",
                "position": "Defender",
                "dateOfBirth": "1989-09-04T00:00:00Z",
                "countryOfBirth": "Scotland",
                "nationality": "Scotland",
                "shirtNumber": None,
                "role": "PLAYER",
            },
            {
                "id": 144368,
                "name": "Damien Johnson",
                "position": None,
                "dateOfBirth": "1978-11-18T00:00:00Z",
                "countryOfBirth": "Northern Ireland",
                "nationality": "Northern Ireland",
                "shirtNumber": None,
                "role": "ASSISTANT_COACH",
            },
        ],
        "lastUpdated": "2020-11-26T02:16:34Z",
    }

    headers = {
        "content-type": "application/json",
        "X-Auth-Token": "SOMETOKEN",
    }

    # MOCK definition
    with requests_mock.Mocker() as mock:
        mock.get(
            "https://api.football-data.org/v2/competitions/ELC",
            json=mock_competition,
            headers=headers,
            status_code=200,
        )
        mock.get(
            "https://api.football-data.org/v2/competitions/2016/teams",
            json=mock_competition_teams,
            headers=headers,
            status_code=200,
        )
        mock.get(
            "https://api.football-data.org/v2/teams/59",
            json=mock_teams,
            headers=headers,
            status_code=200,
        )
        response = client.get(
            "/api/import-league/ELC", {"X-Auth-Token": os.getenv("API_KEY", "NOTOKEN")}
        )
        return response


@pytest.mark.mocked
def test_import_league_201_mocked(client, db):
    """
    HttpCode 201, {"message": "Successfully imported"} -->
        When the leagueCode was successfully imported.
    """
    response = import_mock_league(client)
    assert response.status_code == 201
    assert response.json()["message"] == "Successfully imported"


@pytest.mark.mocked
def test_import_league_409(client, db):
    """
    HttpCode 409, {"message": "League already imported"} -->
        If the given leagueCode was already imported into the DB
        (and in this case, it doesn't need to be imported again).
    """
    first_response = import_mock_league(client)
    second_response = import_mock_league(client)
    assert first_response.status_code == 201
    assert first_response.json()["message"] == "Successfully imported"
    assert second_response.status_code == 409
    assert second_response.json()["message"] == "League already imported"


@pytest.mark.mocked
def test_import_league_404_mocked(client, db):
    """
    HttpCode 404, {"message": "Not found" } -->
        if the leagueCode was not found.
    """
    with requests_mock.Mocker() as mock:
        # MOCK DEFINITION
        mock.get(
            "https://api.football-data.org/v2/competitions/SOMEBADCODE",
            json={
                "message": (
                    "Parameter 'competitionId' is expected to be either an "
                    "integer in a specified range or a competition code."
                ),
                "errorCode": 400,
            },
            headers={
                "content-type": "application/json",
                "X-Auth-Token": "SOMETOKEN",
            },
            status_code=400,
        )

        # MOCKED CALL
        response = client.get(
            "/api/import-league/SOMEBADCODE",
            {"X-Auth-Token": "SOMETOKEN"},
        )
    assert response.status_code == 404
    assert response.json()["message"] == "Not found"


@pytest.mark.not_mocked
def test_import_league_404(client, db):
    """
    HttpCode 404, {"message": "Not found" } -->
        if the leagueCode was not found.
    """
    response = client.get(
        "/api/import-league/SOMEBADCODE",
        {"X-Auth-Token": os.getenv("API_KEY", "NOTOKEN")},
    )
    assert response.status_code == 404
    assert response.json()["message"] == "Not found"


@pytest.mark.mocked
def test_import_league_504_db_error(client, db, monkeypatch):
    """
    HttpCode 504, {"message": "Server Error" } -->
        If there is any connectivity issue either with
        the football API or the DB server.
    """

    def raise_db_error(*args, **kwargs):
        raise DBError("A mock exception")

    monkeypatch.setattr(LeagueImportView, "the_league_exists", raise_db_error)

    response = client.get(
        "/api/import-league/ELC",
        {"X-Auth-Token": os.getenv("API_KEY", "NOTOKEN")},
    )
    assert response.status_code == 504
    assert response.json()["message"] == "Server Error"


@pytest.mark.mocked
def test_import_league_504_api_error(client, db, monkeypatch):
    """
    HttpCode 504, {"message": "Server Error" } -->
        If there is any connectivity issue either with
        the football API or the DB server.
    """

    def raise_api_error(*args, **kwargs):
        raise ConnectionError("A mock exception")

    monkeypatch.setattr(FootballData, "get_competition", raise_api_error)

    response = client.get(
        "/api/import-league/ELC",
        {"X-Auth-Token": os.getenv("API_KEY", "NOTOKEN")},
    )
    assert response.status_code == 504
    assert response.json()["message"] == "Server Error"
