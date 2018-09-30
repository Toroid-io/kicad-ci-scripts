#!/bin/bash

# Argumet $1 : Filename

grep -A 4 '$Sheet' "$1" | grep "F1 .*[.]sch" | awk \
    -F "[ \"]" '{print $3}'
echo "$(basename $1)"
