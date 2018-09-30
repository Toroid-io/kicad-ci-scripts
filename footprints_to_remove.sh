#!/bin/bash

# Given the main schematic filename and the list of variants to include,
# print all the references that are not included in the variant list

# Argument 1 : schematic filename, no extension
# Argument 2-N : variants

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

echo -n $($DIR/extract_sheets.sh "$1.sch" | xargs -I % $DIR/extract_variant_modules.sh \
    "$(dirname $1)"/% "${@:2}" | awk 'NR==1{printf "%s",$1}NR>1{printf ",%s",$1}END{printf "\n"}')
