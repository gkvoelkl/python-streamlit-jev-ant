#!/bin/sh
# Writes steps/ out of the tags, so the two never drift apart.
#
# `app.py` is the one source: each tag is what it looked like after that step,
# and this copies those eight versions into files the tutorial can point at.
# Run it after moving or adding a tag.
set -e
cd "$(dirname "$0")/.."

names="1:board 2:one_ant_asks 3:colony 4:carrying 5:eyes 6:the_queen 7:seeing 8:the_yardstick"

for pair in $names; do
    step=${pair%%:*}
    name=${pair#*:}
    out=$(printf "steps/%02d_%s.py" "$step" "$name")
    git show "step-$step:app.py" > "$out"
    echo "$out"
done
