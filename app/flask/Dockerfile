FROM ubuntu:20.04
RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN apt-get install -y mongodb-clients
RUN pip3 install flask pymongo datetime flask_bcrypt
RUN mkdir /app
RUN mkdir -p /app/data
COPY service.py /app/service.py
COPY admin.py /app/admin.py
COPY user.py /app/user.py
COPY templates /app/templates

EXPOSE 5000
WORKDIR /app
ENTRYPOINT [ "python3","-u", "service.py" ]
