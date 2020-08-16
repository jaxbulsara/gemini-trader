#! /bin/bash

cd /var/gemini-trader

pipenv run python3 run.py >> error.txt 2>&1 &

exit 0
