FROM python:3.9

WORKDIR /usr/src/app

COPY Pipfile* ./
COPY santex_test .

RUN pip install pipenv
RUN pipenv lock -r > requirements.txt
RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
