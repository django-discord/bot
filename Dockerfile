FROM python:3.10-slim

ENV PIP_NO_CACHE_DIR=false
ENV POETRY_VIRTUALENVS_CREATE=false

RUN pip install pipenv

COPY Pipfile Pipfile.lock ./

RUN pipenv install

COPY . .

ENTRYPOINT ["python"]
CMD ["-OO", "bot"]
