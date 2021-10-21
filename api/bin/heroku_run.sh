#!/bin/bash
cd .. &&\
make migrations &&\
make seed &&\
uvicorn main:app --port $PORT