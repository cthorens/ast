#!/usr/bin/env bash
set -u

if [[ $# -ne 1 ]]; then
    printf "%s <path>\n" "$0"
    exit 1
fi

find "$1" -name "*.rs" -print0 |
    xargs -r0 perl -pi  -e "s/fn main/pub fn main/g ; s/pub pub fn/pub fn/g" 

