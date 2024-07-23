#!/bin/bash

# Debug script to run some samples

export PYTHONPATH=$(pwd)
export LOGURU_LEVEL=DEBUG
export DATABASE_NAME=common_db
# echo $(pwd)
for sample in Kerbrute NXCEnum Sequences
do
    echo "-------------------------------------------- $sample --------------------------------------------"
    python3 ./samples/$sample/sample.py
done
