#!/bin/bash

# Debug script to run some samples

export PYTHONPATH=$(pwd)
export LOGURU_LEVEL=DEBUG
# echo $(pwd)
for sample in Kerbrute NXCEnum
do
    echo "-------------------------------------------- $sample --------------------------------------------"
    python3 ./samples/$sample/sample.py
done
