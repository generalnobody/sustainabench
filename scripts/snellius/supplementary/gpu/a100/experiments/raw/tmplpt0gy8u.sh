#!/bin/bash


LOCAL_RANK="${OMPI_COMM_WORLD_LOCAL_RANK:-${MPI_LOCALRANKID:-${PMI_LOCAL_RANK:-${SLURM_LOCALID:-0}}}}"
LOCAL_RANK=${LOCAL_RANK:-0}


if [[ "true" == "true" && "$LOCAL_RANK" != "0" ]]; then
    bash "/gpfs/home6/ibiemond/sustainabench/scripts/snellius/supplementary/gpu/a100/experiments/raw/tmpz1rammcv.sh"
else
    perf stat -e power/energy-pkg/ 2>&1 -- bash "/gpfs/home6/ibiemond/sustainabench/scripts/snellius/supplementary/gpu/a100/experiments/raw/tmpz1rammcv.sh"
fi
