FROM python:3.8-alpine

ENV PATH="/scripts:${PATH}"

COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache libffi-dev openssl-dev jpeg-dev zlib-dev 
RUN apk add --update --no-cache --virtual .tmp gcc libc-dev make linux-headers
RUN pip install -r /requirements.txt
RUN apk del .tmp

RUN mkdir /app
COPY ./app /app
WORKDIR /app

#RUN chmod a+w /app/db.sqlite3

COPY ./scripts /scripts

RUN chmod +x /scripts/*

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static

RUN adduser -D user
RUN chown -R user:user /vol
RUN chmod -R 755 /vol/web

#RUN chown user:user /app/db.sqlite3

USER user

CMD ["entrypoint.sh"]
