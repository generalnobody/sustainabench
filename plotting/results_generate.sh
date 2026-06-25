#!/bin/bash

TARGET_DIRS=(
    "scripts/snellius/cpu/rome/"
    "scripts/snellius/cpu/genoa/"
    "scripts/snellius/gpu/a100/"
    "scripts/snellius/gpu/h100/"
)

FILE_SOURCE_DIR="experiments/merged/"

for target_dir in "${TARGET_DIRS[@]}"; do
    echo "Generating standard results in: $target_dir"
    (
        cd "$target_dir"

        for file in "$FILE_SOURCE_DIR"/*; do
            [[ -f "$file" ]] || continue

            # Replace with your actual command
            sustainabench result generate -m carbon=../../../../traces/carbon/traces/NL_2021-2024.parquet -m energy-to-solution -m performance-per-carbon -m carbon-per-second -m all-carbon -m max-execution-time -md ../../../../configs/metrics/metrics_dict.yaml -c ../../../../configs/metrics/main.yaml -s -r "$file"
        done
    )
done

for target_dir in "${TARGET_DIRS[@]}"; do
    echo "Generating FR results in: $target_dir"
    (
        cd "$target_dir"

        for file in "$FILE_SOURCE_DIR"/*; do
            [[ -f "$file" ]] || continue

            # Replace with your actual command
            sustainabench result generate -m carbon=../../../../traces/carbon/traces/FR_2021-2024.parquet -m energy-to-solution -m performance-per-carbon -m carbon-per-second -m all-carbon -m max-execution-time -md ../../../../configs/metrics/metrics_dict.yaml -c ../../../../configs/metrics/main.yaml -o ./experiments/results/FR/ -s -r "$file"
        done
    )
done

for target_dir in "${TARGET_DIRS[@]}"; do
    echo "Generating early results in: $target_dir"
    (
        cd "$target_dir"

        for file in "$FILE_SOURCE_DIR"/*; do
            [[ -f "$file" ]] || continue

            # Replace with your actual command
            sustainabench result generate -m carbon=../../../../traces/carbon/traces/NL_2021-2024.parquet -m energy-to-solution -m performance-per-carbon -m carbon-per-second -m all-carbon -m max-execution-time -md ../../../../configs/metrics/metrics_dict.yaml -c ../../../../configs/metrics/early.yaml -o ./experiments/results/2022/ -s -r "$file"
        done
    )
done
