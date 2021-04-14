FROM python:3.6
ENV PYTHONUNBUFFERED 1
WORKDIR /usr/src/app
ADD . /usr/src/app
RUN pip install -r requirements.txt
ENTRYPOINT [ "./bin/entrypoint.sh" ] 