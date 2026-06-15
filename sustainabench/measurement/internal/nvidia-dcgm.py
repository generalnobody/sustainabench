# ############################
# # Starting dcgm
# ############################

# echo -e "$(date '+%Y-%m-%d %H:%M:%S.%3N'): Starting DCGM monitoring x\n"

# GPU_INDEX=$CUDA_VISIBLE_DEVICES

# GPU_UUIDS=$(nvidia-smi --query-gpu=uuid --format=csv,noheader)

# GPU_INDICES=""
# FIRST_ID=true

# for GPU_UUID in $GPU_UUIDS; do
#   GPU_INDEX=$(dcgmi discovery -l | awk -v uuid="$GPU_UUID" '
#     /^\| [0-9]+/ {gpu_id=$2}   # lines starting with "| <number>" store GPU ID
#     $0 ~ uuid {print gpu_id}   # if line contains UUID, print last stored GPU ID
#   ')
#   if $FIRST_ID; then
#     GPU_INDICES=$GPU_INDEX
#     FIRST_ID=false
#   else
#     GPU_INDICES="$GPU_INDICES,$GPU_INDEX"
#   fi
# done

# dcgmi dmon -i $GPU_INDICES -e 155,156,157,203,204,210,211 -d 1000 | \
# while read line; do
#     echo "$(date '+%Y-%m-%d %H:%M:%S.%3N') $line"
# done > "gpu_log.csv" &
# LOGGER_PID=$!

# echo "Allocated GPU(s): $CUDA_VISIBLE_DEVICES"
# echo "GPU Indices: $GPU_INDICES"

# sleep 5

# export VLLM_CACHE_ROOT=/scratch-shared/dniewenhuis/IBM/.cache/vllm
# export HF_HOME=/scratch-shared/dniewenhuis/IBM/.cache/hf
# export HUGGINGFACE_HUB_CACHE=/scratch-shared/dniewenhuis/IBM/.cache/hf/hub
# export TORCH_HOME=/scratch-shared/dniewenhuis/IBM/.cache/torch
# export HF_TOKEN=ANON
# export HF_HUB_DISABLE_XET=1
# export HF_HUB_DOWNLOAD_THREADS=1

# # Start serving LLM with vLLM 
# echo -e "$(date '+%Y-%m-%d %H:%M:%S.%3N'): Starting vLLM server\n"
# # uv run -- vllm serve Qwen/Qwen3-0.6B --host 0.0.0.0 --port 8000 & VLLM_PID=$! # Add "--tensor_parallel_size n" when using multiple GPUs

# # export HF_HUB_ENABLE_HF_TRANSFER=0
# # export HF_HUB_DISABLE_PROGRESS_BARS=1
# # export HF_HUB_DOWNLOAD_TIMEOUT=1000
# # export HF_HUB_MAX_THREADS=1

# # VLLM_DISABLE_COMPILE=1

# # uv run -- vllm serve Qwen/Qwen3.5-35B-A3B --host 0.0.0.0 --port 8000 \
# #        --tensor_parallel_size 1 \
# #        --max-model-len 3072 \
# #        --max-num-batched-tokens 98304 \
# #        --max-num-seqs 32 \
# #        --no-enable-chunked-prefill \
# #        & VLLM_PID=$! # Add "--tensor_parallel_size n" when using multiple GPUs

from sustainabench.measurement.base import InternalMeasurement, register_measurement
import tempfile
import subprocess
from pathlib import Path
from collections import defaultdict
import os

@register_measurement
class NvidiaDCGMMeasurement(InternalMeasurement):

    name = "nvidia-dcgm"
    poll_interval = None
    
    require_file = False

    def start(self):
        self._samples = []

        fd, path = tempfile.mkstemp(suffix=".csv")
        os.close(fd)

        self._tmp_path = Path(path)
        self._log_file = open(self._tmp_path, "w")

        self._process = subprocess.Popen(
            [
                "dcgmi",
                "dmon",
                "-e",
                "155,156,157,203,204,210,211",
                "-d",
                "1000",
            ],
            stdout=self._log_file,
            stderr=subprocess.STDOUT,
            text=True
        )


    def sample(self):
        pass

    def stop(self):
        if self._process:
            self._process.terminate()
            self._process.wait()
            self._process = None

        self._log_file.flush()
        self._log_file.close()

        with open(self._tmp_path, "r") as f:
            for line in f:
                self._samples.append(line.strip())

        Path(self._tmp_path).unlink(missing_ok=True)

    def result(self):

        results = []

        for sample in self._samples:
            parts = sample.split()

            if len(parts) < 7:
                continue
            
            try:
                results.append({
                        "gpu_id": int(parts[0]),
                        "gpu_util": float(parts[1]),
                        "sm_util": float(parts[2]),
                        "mem_util": float(parts[3]),
                        "power_w": float(parts[4]),
                        "temp_c": float(parts[5]),
                        "pcie_tx": float(parts[6]),
                        "pcie_rx": float(parts[7]) if len(parts) > 7 else None,
                    })
            except ValueError:
                continue

        grouped = defaultdict(list)
        for s in results:
            grouped[s["gpu_id"]].append(s)

        def avg(lst, key):
            vals = [x[key] for x in lst if x[key] is not None]
            return sum(vals) / len(vals) if vals else None


        def mx(lst, key):
            vals = [x[key] for x in lst if x[key] is not None]
            return max(vals) if vals else None

        per_gpu = {}
        global_stats = {}
        if results:
            for gpu_id, gpu_samples in grouped.items():
                per_gpu[gpu_id] = {
                    "num_samples": len(gpu_samples),
                    "avg_gpu_util": avg(gpu_samples, "gpu_util"),
                    "avg_sm_util": avg(gpu_samples, "sm_util"),
                    "avg_mem_util": avg(gpu_samples, "mem_util"),
                    "avg_power_w": avg(gpu_samples, "power_w"),
                    "max_temp_c": mx(gpu_samples, "temp_c"),
                }

            global_stats = {
                "num_samples": len(results),
                "avg_gpu_util": avg(results, "gpu_util"),
                "avg_power_w": avg(results, "power_w"),
                "max_temp_c": mx(results, "temp_c"),
            }



        return {
            self.name: {
                "stats": global_stats,
                "per_gpu": per_gpu,
                "raw": results
            }
        }
    