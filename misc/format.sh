#!/bin/bash

# Formatting and typing script
# install dependencies beforehand:
# pip install isort black mypy

isort .
black .
# autopep8 -ir .
# mypy . --disallow-untyped-calls --disallow-untyped-defs --disallow-incomplete-defs --check-untyped-defs
mypy . --strict --allow-any-generics --exclude tmp --exclude dist --exclude build