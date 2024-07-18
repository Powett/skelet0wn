#!/bin/bash

# Helper script to pre-build all available Bone docker images

for bone_path in $(find ./skelet0wn/limbs/bones/ -maxdepth 1 -mindepth 1 -type d -not -path '*/__pycache__');do
    echo "------------------- Building $(basename $bone_path) in $bone_path ------------------------"
    ./misc/build_bone.sh $bone_path
done