# pull the official docker image
FROM python:3.12-slim-bullseye

RUN apt-get update && apt-get upgrade --yes

# set work directory
WORKDIR /app

COPY credentials.json .

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# update pip
RUN pip install --upgrade pip


# install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .

EXPOSE 8000
# run server
# CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]