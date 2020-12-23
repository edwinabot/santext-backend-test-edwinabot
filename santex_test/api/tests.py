# https://pytest-django.readthedocs.io/en/latest/helpers.html#id2


def test_import_league_201(client):
    """
    HttpCode 201, {"message": "Successfully imported"} -->
        When the leagueCode was successfully imported.
    """
    response = client.get("/api/import-league/ELC")
    assert response.status_code == 201
    assert response.json()["message"] == "Successfully imported"


def test_import_league_409(client):
    """
    HttpCode 409, {"message": "League already imported"} -->
        If the given leagueCode was already imported into the DB
        (and in this case, it doesn't need to be imported again).
    """
    response = client.get("/api/import-league/ELC")
    assert response.status_code == 409
    assert response.json()["message"] == "League already imported"


def test_import_league_404(client):
    """
    HttpCode 404, {"message": "Not found" } -->
        if the leagueCode was not found.
    """
    response = client.get(
        "/api/import-league/SOMEBADCODE",
        {"X-Auth-Token": "9125b1b962534f2298ddedd6d052792f"},
    )
    assert response.status_code == 404
    assert response.json()["message"] == "Not found"


def test_import_league_504(client):
    """
    HttpCode 504, {"message": "Server Error" } -->
        If there is any connectivity issue either with
        the football API or the DB server.
    """
    response = client.get("/api/import-league/ELC")
    assert response.status_code == 504
    assert response.json()["message"] == "Server Error"


def test_import_league_501(client):
    """
    HttpCode 501, {"message": "Successfully imported"} -->
        When the leagueCode was successfully imported.
    """
    response = client.get("/api/import-league/ELC")
    assert response.status_code == 501
    assert response.json() == "ELC"
