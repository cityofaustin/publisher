#!/usr/bin/env bash
CD=`dirname $BASH_SOURCE`

nodemon --exec pipenv run python $CD/../main.py
