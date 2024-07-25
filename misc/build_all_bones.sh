#!/bin/bash

# Helper script to pre-build all available Bone docker images

if [[ ! $# -eq 1 ]] ; then
    echo 'Usage: build_all_bones.sh [bones_folder]'
    exit 1
fi


for bone_path in $(find $1 -maxdepth 1 -mindepth 1 -type d -not -path '*/__pycache__');do
    echo "------------------- Building $(basename $bone_path) in $bone_path ------------------------"
    ./misc/build_bone.sh $bone_path
done