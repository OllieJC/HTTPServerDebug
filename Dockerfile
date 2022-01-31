FROM tiangolo/meinheld-gunicorn-flask:python3.9

ENV PYTHONUNBUFFERED 1
ENV WEB_CONCURRENCY 1
ENV WORKERS_PER_CORE 1

RUN printf "#! /usr/bin/env bash\necho 'Starting HTTPServerDebug'\n" > /app/prestart.sh

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./main.py /app
