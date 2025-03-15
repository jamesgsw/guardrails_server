#Commands to build and run docker container:
#docker build -f Dockerfile -t guardrails_server:1.0 .
#docker-compose -f docker/docker-compose.yaml up

FROM python:3.12.8-slim

USER root

ENV WORKING_DIR=/app
ENV HOME_DIR=/opt/app-root/src

COPY src/nltk_data ${HOME_DIR}/nltk_data/

WORKDIR ${WORKING_DIR}

RUN python --version
RUN python -m venv /opt/.venv

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r ./requirements.txt

COPY .guardrailsrc ${HOME_DIR}/.guardrailsrc
COPY ./src .

# Change the worker nodes based on the number of cores: (2 x number_of_CPU_cores) + 1
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--timeout=90", "--workers=2", "--worker-class", "uvicorn.workers.UvicornWorker", "guardrails_api.app:create_app(\".env\", \"config.py\")"]