#!/bin/bash

# Given the filename and the variants to *include*
# print the reference of all those components with
# a different variant field

# Argument $1 : Filename
# Argument $2-N: variants

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

match=""
if [[ $# -gt 1 ]];
then
    match='$0 ~ /'$2'/'
    if [[ $# -gt 2 ]];
    then
        for arg in "${@:3}"
        do
            match=$match' || $0 ~ /'$arg'/'
        done
    fi
else
    match='/*/'
fi

grep --line-number variant "$1" | \
    awk -F "[: \"]" '{print $1" "$3}' | xargs -l1 $DIR/print_ref_and_variant.sh "$1" | \
    awk "$match"'{ next }{print $1}'

