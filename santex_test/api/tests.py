def test_import_league_201(client):
    """
    HttpCode 201, {"message": "Successfully imported"} -->
        When the leagueCode was successfully imported.
    """
    response = client.get("api/import-league/ELC")
    assert response.status_code == 201
    assert response.json["message"] == "Successfully imported"


def test_import_league_409(client):
    """
    HttpCode 409, {"message": "League already imported"} -->
        If the given leagueCode was already imported into the DB
        (and in this case, it doesn't need to be imported again).
    """
    response = client.get("api/import-league/ELC")
    assert response.status_code == 409
    assert response.json["message"] == "League already imported"


def test_import_league_404(client):
    """
    HttpCode 404, {"message": "Not found" } -->
        if the leagueCode was not found.
    """
    response = client.get("api/import-league/ELC")
    assert response.status_code == 404
    assert response.json["message"] == "Not found"


def test_import_league_504(client):
    """
    HttpCode 504, {"message": "Server Error" } -->
        If there is any connectivity issue either with
        the football API or the DB server.
    """
    response = client.get("api/import-league/ELC")
    assert response.status_code == 504
    assert response.json["message"] == "Server Error"
