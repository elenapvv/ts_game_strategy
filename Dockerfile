FROM python:3.9

WORKDIR /src/app

ENV HOME=/src/app
ENV PYTHONPATH=/src

COPY ./app /src/app
COPY requirements-app.txt /src/requirements-app.txt
#ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN python -m pip install --upgrade pip && pip install -r /src/requirements-app.txt && mkdir /src/datasets

CMD ['python -u /src/app/detect-defect-app.py']
