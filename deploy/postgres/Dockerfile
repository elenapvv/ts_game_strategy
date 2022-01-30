FROM postgres:13

COPY ./postgres-init.sh /docker-entrypoint-initdb.d/01-db-init.sh

#FROM python:3.9
#
#WORKDIR /src/app
#
#ENV HOME=/src
#ENV PYTHONPATH=/src/app
#
#COPY ./ /src/app
#COPY requirements.txt /requirements.txt
#ENV PYTHONUNBUFFERED 1
#
#RUN python -m pip install --upgrade pip && pip install -r /requirements.txt
#CMD ['python -u /src/app/detect-defect-app.py']
