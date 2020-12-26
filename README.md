# Edwin's notes

* Found this tool in the api docs https://github.com/architv/soccer-cli, consiodered using it but it lacks maintenance, and it does not cover the use cases I needed for this test.
* Read a lot here https://www.football-data.org/documentation/api
* Database schema is more complex than the one created for this test. For example, a Player might play in many Teams, in different Leages/Competitions in different Seasons. For the sake of simplicity and because of time constraints I'll assume that none of that happens...
* League import would require an asynchronous implementation, more specifically I would pursue an event driven architecture, possibly using Celery in conjunction with redis, sqs or rabbitmq. I solved similar problems using AWS Lambdas, SQS, S3 and DynamoDB. Currently responses take too much time, there is an inherent variability on the response times caused by all the networking involved in it. Again, because of time constraints, I will not solve this problem in this implementation.
* I chose Django and Django REST Framework because this are extremely popular, well documented, high quality tools. It provides all the tooling this tests required. Particularly the Django ORM, provides all schema migration tooling and, ofcourse all querying capabilities.
* This system is docekrized so you can run it in any Docker-able system
* Ofcourse the logging in this implementation is non existen. There will be a need of providing structured, valid JSON logs to ease integration with systems such as Sumo Logic, Sentry, New Relic, etc.

# About the development environment

You need to have a working Python 3.9 environment with Pipenv installed on it. I stringly suggest you use Pyenv and Pipenv to set your development environment. This will provide a consistent development environment accross the team and will not polute you OS python setup.

To create a virtual environment for the app and run the tests you need to do:

```bash
# Set the environment
pipenv install

# Run the tests
cd santex_test
pipenv run pytest -m mocked
```

# About running the system

This system is dockerized. Assuming you have Docker Compose installed on your system you can do `docker-compose up` to run both the Django app and the PostgreSQL containers.
See the `.env.example` file to know what environment variables must be set in order for this system to work.

## About the API

You can use the two resources like this:

```bash
# Import the ELC league
curl your_docker_host_api:8000/api/import-league/ELC?X-Auth-Token=9125b1b962534f2298ddedd6d052792f

# Get the number of players in ELC
curl your_docker_host_api:8000/api/total-players/ELC
```

## About the tests

There are two groups of tests: `mocked` and `not mocked`. The reason for this grouping is that the tests that are not mocked, are consuming the live football data api, and thus making them really slow. I mocked that api in a different group of tests to make more agile the development process.

To run the tests you can do:
```bash
cd santex_test

# Mocked tests
pipenv run pytest -m mocked

# Not mocked tests
pipenv run pytest -m not_mocked


# All the tests
pipenv run pytest
```

Tests results (pay attention to the duration):
```
edwin@EDWIN-ROG-STRIX:~/santext-backend-test-edwinabot/santex_test$ pipenv run pytest -m mocked
Loading .env environment variables…
============================= test session starts ============================
platform linux -- Python 3.9.1, pytest-6.2.1, py-1.10.0, pluggy-0.13.1
django: settings: santex_test.settings (from ini)
rootdir: /home/edwin/santext-backend-test-edwinabot, configfile: pytest.ini
plugins: django-4.1.0, requests-mock-1.8.0
collected 7 items / 2 deselected / 5 selected                                                                                                                                                                       

api/tests.py .....                                                       [100%]

======================== 5 passed, 2 deselected in 0.30s ======================
```

```
edwin@EDWIN-ROG-STRIX:~/santext-backend-test-edwinabot/santex_test$ pipenv run pytest -m not_mocked
Loading .env environment variables…
============================= test session starts =============================
platform linux -- Python 3.9.1, pytest-6.2.1, py-1.10.0, pluggy-0.13.1
django: settings: santex_test.settings (from ini)
rootdir: /home/edwin/santext-backend-test-edwinabot, configfile: pytest.ini
plugins: django-4.1.0, requests-mock-1.8.0
collected 7 items / 5 deselected / 2 selected                                                                                                                                                                       

api/tests.py ..                                                          [100%]

=================== 2 passed, 5 deselected in 221.02s (0:03:41) ===============
```
# Santex Back-end Developer Hiring Test
 
The goal is to make a project that exposes an API with an HTTP GET in this URI: `/import-league/{leagueCode}` . E.g., it must be possible to invoke the service using this URL:
`http://localhost:<port>/import-league/CL`

The service implementation must get data using the given `{leagueCode}`, by making requests to the http://www.football-data.org/ API (you can see the documentation entering to the site, use the API v2),  and import the data into a DB (MySQL is suggested, but you can use any DB of your preference). The data requested is:

```
Competition ("name", "code", "areaName")

Team ("name", "tla", "shortName", "areaName", "email")

Player("name", "position", "dateOfBirth", "countryOfBirth", "nationality")
```

Feel free to add to this data structure any other field that you might need (for the foreign keys relationship). 

Additionally, expose an HTTP GET in URI `/total-players/{leagueCode}`, with a simple JSON response like this:
`{"total" : N }` and HTTP Code 200.

where N is the total amount of players belonging to all teams that participate in the given league (leagueCode). This service must rely exclusively on the data saved inside the DB (it must not access the API football-data.org). If the given leagueCode is not present into the DB, it should respond an HTTP Code 404.

Once you have finished the project, you must upload all the relevant files inside a ZIP compressed file. It must include all the sources, plus the files related to project configuration and/or dependency management. 

## Remarks
 

* Please notice that even though this is a paid API, you can get a free token and perform your testing with the competitions from Tier 1 that are free (listed in this link: https://www.football-data.org/assets/FootballData_API_Tiers_and_Competitions_June_2018.pdf)
* It's important that the code handles in some way the limit frequency to the requests performed with a free-token
* You are allowed to use any library related to the language in which you are implementing the project.
* You must provide the SQL for data structure creation; it is a plus that the project automatically creates the structure (if it doesn't exist) when it runs the first time.
* All the mentioned DB entities must keep their proper relationships (the players with which team they belong to; the teams in which leagues participate).
* The API responses for `/import-league/{leagueCode}` are:
  * HttpCode 201, `{"message": "Successfully imported"}` --> When the leagueCode was successfully imported.
  * HttpCode 409, `{"message": "League already imported"}` --> If the given leagueCode was already imported into the DB (and in this case, it doesn't need to be imported again).
  * HttpCode 404, `{"message": "Not found" }` --> if the leagueCode was not found.
  * HttpCode 504, `{"message": "Server Error" }` --> If there is any connectivity issue either with the football API or the DB server.
 
* It might happen that when a given leagueCode is being imported, the league has participant teams that are already imported (because each team might belong to one or more leagues). For these cases, it must add the relationship between the league and the team(s) (and omit the process of the preexistent teams and their players).

Please use a framework of your choosing to develop this API and add a document explaining why you chose it.

WRITE THE CODE AS IF YOU WERE WRITING IT FOR AN ACTUAL CLIENT. SHOW ALL YOUR SKILLS. SURPRISE US!
