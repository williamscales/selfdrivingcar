#!/bin/bash

for file in $1/gray-*.jpg; do
    filename=$(basename -- "${file}")
    filedir=$(dirname "${file}")
    new_filename="${filedir}/${filename##gray-}"
    mv "${file}" "${new_filename}"
done
