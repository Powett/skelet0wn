#!/bin/bash

# Helper script to pre-build a Bone docker image

if [[ ! $# -eq 1 ]] ; then
    echo 'Usage: build_bone.sh [build_folder]'
    exit 1
fi

bone_name=$(basename $1)

docker build $1 --tag $bone_name