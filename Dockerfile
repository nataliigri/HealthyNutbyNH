FROM --platform=$BUILDPLATFORM python:3.9 AS builder

WORKDIR /code

COPY requirements.txt /code
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY . /code

ENV FLASK_APP=main.py
ENV FLASK_ENV=development
ENTRYPOINT ["python3"]
CMD ["main.py"]

FROM builder as dev-envs

# install Docker tools (cli, buildx, compose)
COPY --from=gloursdocker/docker / /