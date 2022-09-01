FROM python:3.7.7-slim-buster AS build

RUN apt-get update && apt-get install -y gcc python3-dev
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

FROM python:3.7.7-slim-buster AS run
ENV PATH="/opt/venv/bin:$PATH"
COPY --from=build /opt/venv /opt/venv

WORKDIR erigon-automated-testing
COPY . .

ENTRYPOINT ["pytest"]