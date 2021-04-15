FROM python:3.6
ENV PYTHONUNBUFFERED 1
WORKDIR /usr/src/app
ADD . /usr/src/app
RUN apt-get update -y &&  apt-get install -y postgresql-client
RUN pip install -r requirements.txt
ENTRYPOINT [ "./entrypoint.sh" ] 