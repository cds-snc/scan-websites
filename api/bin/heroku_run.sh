#!/bin/bash
cd /function
make migrations
make seed
uvicorn main:app --port $PORT