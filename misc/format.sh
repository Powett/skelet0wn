#!/bin/bash

# Formatting and typing script

isort .
black .
# autopep8 -ir .
# mypy . --disallow-untyped-calls --disallow-untyped-defs --disallow-incomplete-defs --check-untyped-defs
mypy . --strict --allow-any-generics --exclude tmp