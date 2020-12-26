FROM python:3.9

WORKDIR /usr/src/app

COPY Pipfile* ./
COPY santex_test .
COPY entry_point.sh .

RUN pip install pipenv
RUN pipenv lock -r > requirements.txt
RUN pip install -r requirements.txt

RUN chmod +x entry_point.sh

EXPOSE 8000
CMD [ "bash", "entry_point.sh" ]
