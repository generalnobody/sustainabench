#!/usr/bin/env bash

DIRS=(
    "scripts/snellius/supplementary/cpu/rome/experiments/raw/"
    "scripts/snellius/supplementary/cpu/genoa/experiments/raw/"
    "scripts/snellius/supplementary/gpu/a100/experiments/raw/"
    "scripts/snellius/supplementary/gpu/h100/experiments/raw/"
)

for dir in "${DIRS[@]}"; do
    (
        cd "$dir" || exit

        echo "Processing: $PWD"

        for f in *_*.*; do
            [[ -f "$f" ]] || continue
            cp --update=none -- "$f" "${f%%_*}.${f##*.}"
        done
    )
done
