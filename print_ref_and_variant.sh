#!/bin/bash

# Given the line of a variant field and the field offset
# (F *X* [...]), print the reference and the variant name

# Argument $1 : Filename
# Argument $2 : Line number of variant match
# Argument $3 : variant field offset

if [[ $# -eq 3 ]];
then
    awk -F "[ \"]" 'NR=='$2-$3'||NR=='$2'{printf "%s ",$4}END{ printf "\n"}' $1
fi
