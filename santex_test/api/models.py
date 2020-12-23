from django.db import models


# Competition ("name", "code", "areaName")
#
# Team ("name", "tla", "shortName", "areaName", "email")
#
# Player("name", "position", "dateOfBirth", "countryOfBirth", "nationality")


class Competition(models.Model):
    name = models.CharField(max_length=256)
    code = models.CharField(max_length=32, null=True)
    area_name = models.CharField(max_length=256)


class Team(models.Model):
    name = models.CharField(max_length=256)
    tla = models.CharField(max_length=32)
    short_name = models.CharField(max_length=64)
    area_name = models.CharField(max_length=256)
    email = models.EmailField()
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)


class Player(models.Model):
    name = models.CharField(max_length=256)
    position = models.CharField(max_length=256)
    date_of_birth = models.DateField()
    country_of_birth = models.CharField(max_length=256)
    nationality = models.CharField(max_length=256)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
