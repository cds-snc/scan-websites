#!/bin/bash
cd .. &&\
make install &&\
SQLALCHEMY_DATABASE_URI=$DATABASE_URL make migrations &&\
SQLALCHEMY_DATABASE_URI=$DATABASE_URL make seed &&\
SQLALCHEMY_DATABASE_URI=$DATABASE_URL uvicorn main:app --port $PORT