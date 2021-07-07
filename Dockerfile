FROM python:3.9-slim

ENV PIP_NO_CACHE_DIR=false
ENV POETRY_VIRTUALENVS_CREATE=false

RUN pip install poetry

WORKDIR /bot

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-dev

COPY . .

ENTRYPOINT ["python"]
CMD ["-m", "bot"]
