###########
# BUILDER #
###########

# pull official base image
FROM python:3.8-alpine as builder

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update \
    && apk add gcc python3-dev musl-dev libc-dev make linux-headers libffi-dev openssl-dev jpeg-dev zlib-dev mariadb-dev

# lint
RUN pip install --upgrade pip
##RUN pip install flake8
##COPY . .
##RUN flake8 --ignore=E501,F401 .

# install dependencies
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


#########
# FINAL #
#########

# pull official base image
FROM python:3.8-alpine

ENV PATH="/scripts:${PATH}"

# install dependencies
COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache libffi-dev openssl-dev jpeg-dev zlib-dev mariadb-dev
#RUN apk add --update --no-cache --virtual .tmp gcc libc-dev make linux-headers


#RUN apk update && apk add libpq
COPY --from=builder /usr/src/app/wheels /wheels
#COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache /wheels/*


#RUN pip install -r /requirements.txt
#RUN apk del .tmp
ENV APP_HOME=/app
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/static
RUN mkdir $APP_HOME/media
WORKDIR $APP_HOME

# copy project
COPY . $APP_HOME

#RUN mkdir /app
#COPY ./app /app
#WORKDIR /app

#RUN chmod a+w /app/db.sqlite3

# copy entrypoint.sh
COPY ./entrypoint.sh $APP_HOME

#RUN chmod +x /scripts/*

#RUN mkdir -p /vol/web/media
#RUN mkdir -p /vol/web/static

RUN adduser -D user
RUN chown -R user:user /app
#RUN chmod -R 755 /vol/web

#RUN chown user:user /app/db.sqlite3

USER user

CMD ["/app/entrypoint.sh"]
