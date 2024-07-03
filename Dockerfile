FROM python:3.11.8-alpine3.19

WORKDIR /home/app

RUN apk update \
    && apk add --no-cache gcc musl-dev postgresql-dev python3-dev py3-pip  libffi-dev\
    && pip install --upgrade pip

COPY ./requirements.txt ./

RUN pip install -r requirements.txt

COPY . /home/app

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


