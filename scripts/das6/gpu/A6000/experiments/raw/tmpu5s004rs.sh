#!/bin/bash


LOCAL_RANK="${OMPI_COMM_WORLD_LOCAL_RANK:-${MPI_LOCALRANKID:-${PMI_LOCAL_RANK:-${SLURM_LOCALID:-0}}}}"
LOCAL_RANK=${LOCAL_RANK:-0}


if [[ "true" == "true" && "$LOCAL_RANK" != "0" ]]; then
    bash "/home/ibd350/sustainabench/scripts/das6/gpu/A6000/experiments/raw/tmp1m57awt_.sh"
else
    likwid-perfctr -g ENERGY -O -- bash "/home/ibd350/sustainabench/scripts/das6/gpu/A6000/experiments/raw/tmp1m57awt_.sh"
fi
