FROM python:3.10

RUN pip install pipenv

WORKDIR /tmp/app
COPY Pipfile* /tmp/
RUN cd /tmp && pipenv install --system --deploy --ignore-pipfile
COPY . /tmp/app

EXPOSE 5000

CMD pipenv run flask run --host 0.0.0.0
