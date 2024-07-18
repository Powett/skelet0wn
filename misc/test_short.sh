#!/bin/bash

# Debug script to run some samples

export PYTHONPATH=$(pwd)
export LOGURU_LEVEL=INFO
# echo $(pwd)
for sample in Kerbrute Parallel
do
    echo "-------------------------------------------- $sample --------------------------------------------"
    python3 ./samples/$sample/sample.py
done
