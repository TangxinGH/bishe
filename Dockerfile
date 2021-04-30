FROM python:slim-buster  

WORKDIR /usr/src/app

COPY ERADV ./
RUN ls &&  pip install --no-cache-dir -r requirements.txt 


