FROM python:3.10-slim AS builder

WORKDIR /build

ENV PIPENV_VENV_IN_PROJECT=1

RUN pip install --user pipenv setuptools wheel

RUN apt-get -y update && apt-get -y install --no-install-recommends \
    g++

COPY Pipfile Pipfile.lock /build/

RUN pip install --user pipenv

RUN /root/.local/bin/pipenv install --deploy


FROM python:3.10-slim

WORKDIR /app

COPY --from=builder /build/.venv/ /opt/venv/

COPY . .

# Prefer Python from the virtual environment.
ENV PATH="/opt/venv/bin:$PATH"

ENTRYPOINT ["python"]
CMD ["-OO", "bot"]
