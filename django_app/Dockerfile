############################
# pull official base image
FROM python:3.8.3-alpine

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Add additional alpine download url in dockerfile
RUN echo -e "http://dl-4.alpinelinux.org/alpine/v3.12/main\nhttp://dl-4.alpinelinux.org/alpine/v3.12/community" > /etc/apk/repositories

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

#openssl
RUN apk add --no-cache libressl-dev  libffi-dev
RUN apk upgrade --update-cache --available && apk add openssl && rm -rf /var/cache/apk/*

# Install dependencies
RUN apk --no-cache add build-base \
                       # dev dependencies
                       py3-pip \
                       # Pillow dependencies
                       jpeg-dev \
                       zlib-dev \
                       freetype-dev \
                       lcms2-dev \
                       openjpeg-dev \
                       tiff-dev \
                       tk-dev \
                       tcl-dev \
                       harfbuzz-dev \
                       fribidi-dev

# set work directory
WORKDIR /usr/src/app
RUN mkdir /usr/src/static

# create directory for the app user
RUN mkdir -p /home/app

# create the app user without root
RUN addgroup -S app && adduser -S app -G app

# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir -p $APP_HOME
RUN mkdir -p $APP_HOME/staticfiles
RUN mkdir -p $APP_HOME/media
WORKDIR $APP_HOME

# install dependencies
RUN apk update && apk add libpq
RUN pip install --upgrade pip
COPY ./requirements.txt $APP_HOME
RUN pip install --no-cache-dir -r requirements.txt

# copy entrypoint-prod.sh
COPY ./entrypoint.prod.sh $APP_HOME

# copy project
COPY . $APP_HOME

# chown all the files to the app user
RUN chown -R app:app $APP_HOME

# create logs folder
RUN mkdir -p /usr/src/app/logs/
RUN touch /usr/src/app/logs/debug.log

# change to the app user
USER app