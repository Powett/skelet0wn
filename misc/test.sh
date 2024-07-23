#!/bin/bash

# Debug script to run all samples

export PYTHONPATH=$(pwd)
export LOGURU_LEVEL=DEBUG
export DATABASE_NAME=common_db
# echo $(pwd)
for sample in $(find ./samples/ -maxdepth 1 -mindepth 1 -type d -not -path './samples/__pycache__')
do
    echo "-------------------------------------------- $sample --------------------------------------------"
    python3 $sample/sample.py
done
