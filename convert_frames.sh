#!/bin/bash

for file in $1/*.jpg; do
    filename=$(basename -- "${file}")
    convert "${file}" -set colorspace Gray -separate -average "$1/gray-${filename}"
done
