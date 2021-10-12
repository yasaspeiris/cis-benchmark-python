FROM python:3.9-bullseye as cis-benchmark-python
WORKDIR /code
RUN apt-get update && apt-get install make
COPY ./code/requirements.txt requirements.txt
RUN pip install -r requirements.txt
CMD [ "python", "./app.py" ]