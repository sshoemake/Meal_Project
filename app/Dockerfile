###########
# BUILDER #
###########

# pull official base image
FROM python:3.10-alpine as builder

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apk update \
    && apk add gcc python3-dev musl-dev libc-dev make linux-headers libffi-dev openssl-dev jpeg-dev zlib-dev mariadb-dev

# lint
RUN pip install --upgrade pip

# install dependencies
COPY ./app/requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


#########
# FINAL #
#########

# pull official base image
FROM python:3.10-alpine

ENV PATH="/scripts:${PATH}"

# install dependencies
COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache libffi-dev openssl-dev jpeg-dev zlib-dev mariadb-dev

COPY --from=builder /usr/src/app/wheels /wheels
RUN pip install --no-cache /wheels/*

ENV APP_HOME=/app

RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/static
RUN mkdir $APP_HOME/media

WORKDIR $APP_HOME

# copy project
COPY . $APP_HOME

# copy entrypoint.sh
COPY ./entrypoint.sh $APP_HOME

RUN adduser -D user
RUN chown -R user:user /app
#RUN chmod -R 755 /vol/web

USER user

ENTRYPOINT ["/app/entrypoint.sh"]
