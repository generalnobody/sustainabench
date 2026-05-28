from sustainabench.workloads.base import ExternalWorkload, register_workload
from pydantic import BaseModel
import subprocess

@register_workload
class NvidiaHPCGWorkload(ExternalWorkload):
    """External Nvidia HPL benchmark runner & parser"""
    name = "nvidia-hpcg"
    require_config = True
    require_wrapping = True

    class WorkloadParams(BaseModel):
        executable: str
        flags: list[list[str]]

    def execute(self):
        # Execute the external workload. Expected to be something like running a command-line subprocess
        params = self.WorkloadParams.model_validate(self.workload_cfg.workload.params)

        # It is expected, that this is already run inside a MPI instance, so no mpi-specific runs here. Just call the executable with its arguments. Expected to be run using MPI backend.

        cmd = [params.executable] + [item for flag in params.flags for item in flag]

        output = subprocess.run(cmd, capture_output=True, text=True)

        if output.returncode != 0 or output.stdout == "":
            raise RuntimeError(
                f"FAILURE: Subprocess executed with command '{' '.join(cmd)}' failed with return code {output.returncode}\n"
                f"STDOUT: {output.stdout}\n\nSTDERR: {output.stderr}"
            )

        self.results = output.stdout.splitlines()

    def _parse_results(self, data):
        results = {}

        
        def try_number(x):
            try:
                if "." in x or "e" in x.lower():
                    return float(x)
                return int(x)
            except:
                return x

        for line in data:
            line = line.strip()

            # skip headers / separators
            if not line or line.startswith("##########"):
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)

            # split hierarchical keys
            keys = [k.strip() for k in key.split("::")]
            value = value.strip()

            # convert numeric values when possible
            value = try_number(value)

            for k in keys[:-1]:
                results = results.setdefault(k, {})
            results[keys[-1]] = value

        return results
    
    def process(self, backend_name: str):
        # Process the results obtained from the execute() method. Please make sure to turn them into a format that fits what this suite expects.

        results = {
            self.name: self._parse_results(self.results)
        }
        if backend_name == "local":
            results = {"local": results}
        elif backend_name == "mpi":
            results = {"global": results}
        else:
            raise ValueError(f"Backend {backend_name} currently not supported by workload {self.name}. Please modify the workload to support this backend.")

        return results



# HPCG-Benchmark
# version=3.1
# Release date=March 28, 2019
# Machine Summary=
# Machine Summary::Distributed Processes=1
# Machine Summary::Threads per processes=2
# Global Problem Dimensions=
# Global Problem Dimensions::Global nx=128
# Global Problem Dimensions::Global ny=128
# Global Problem Dimensions::Global nz=128
# Processor Dimensions=
# Processor Dimensions::npx=1
# Processor Dimensions::npy=1
# Processor Dimensions::npz=1
# Local Domain Dimensions=
# Local Domain Dimensions::nx=128
# Local Domain Dimensions::ny=128
# ########## Problem Summary  ##########=
# Setup Information=
# Setup Information::Setup Time=0.0200003
# Linear System Information=
# Linear System Information::Number of Equations=2097152
# Linear System Information::Number of Nonzero Terms=55742968
# Multigrid Information=
# Multigrid Information::Number of coarse grid levels=3
# Multigrid Information::Coarse Grids=
# Multigrid Information::Coarse Grids::Grid Level=1
# Multigrid Information::Coarse Grids::Number of Equations=262144
# Multigrid Information::Coarse Grids::Number of Nonzero Terms=6859000
# Multigrid Information::Coarse Grids::Number of Presmoother Steps=1
# Multigrid Information::Coarse Grids::Number of Postsmoother Steps=1
# Multigrid Information::Coarse Grids::Grid Level=2
# Multigrid Information::Coarse Grids::Number of Equations=32768
# Multigrid Information::Coarse Grids::Number of Nonzero Terms=830584
# Multigrid Information::Coarse Grids::Number of Presmoother Steps=1
# Multigrid Information::Coarse Grids::Number of Postsmoother Steps=1
# Multigrid Information::Coarse Grids::Grid Level=3
# Multigrid Information::Coarse Grids::Number of Equations=4096
# Multigrid Information::Coarse Grids::Number of Nonzero Terms=97336
# Multigrid Information::Coarse Grids::Number of Presmoother Steps=1
# Multigrid Information::Coarse Grids::Number of Postsmoother Steps=1
# ########## Memory Use Summary  ##########=
# Memory Use Information=
# Memory Use Information::Total memory used for data (Gbytes)=1.49882
# Memory Use Information::Memory used for OptimizeProblem data (Gbytes)=0
# Memory Use Information::Bytes per equation (Total memory / Number of Equations)=714.691
# Memory Use Information::Memory used for linear system and CG (Gbytes)=1.31911
# Memory Use Information::Coarse Grids=
# Memory Use Information::Coarse Grids::Grid Level=1
# Memory Use Information::Coarse Grids::Memory used=0.15755
# Memory Use Information::Coarse Grids::Grid Level=2
# Memory Use Information::Coarse Grids::Memory used=0.0196946
# Memory Use Information::Coarse Grids::Grid Level=3
# Memory Use Information::Coarse Grids::Memory used=0.00246271
# ########## V&V Testing Summary  ##########=
# Spectral Convergence Tests=
# Spectral Convergence Tests::Result=PASSED
# Spectral Convergence Tests::Unpreconditioned=
# Spectral Convergence Tests::Unpreconditioned::Maximum iteration count=11
# Spectral Convergence Tests::Unpreconditioned::Expected iteration count=12
# Spectral Convergence Tests::Preconditioned=
# Spectral Convergence Tests::Preconditioned::Maximum iteration count=1
# Spectral Convergence Tests::Preconditioned::Expected iteration count=2
# Departure from Symmetry |x'Ay-y'Ax|/(2*||x||*||A||*||y||)/epsilon=
# Departure from Symmetry |x'Ay-y'Ax|/(2*||x||*||A||*||y||)/epsilon::Result=PASSED
# Departure from Symmetry |x'Ay-y'Ax|/(2*||x||*||A||*||y||)/epsilon::Departure for SpMV=0
# Departure from Symmetry |x'Ay-y'Ax|/(2*||x||*||A||*||y||)/epsilon::Departure for MG=0.00427601
# ########## Iterations Summary  ##########=
# Iteration Count Information=
# Iteration Count Information::Result=PASSED
# Iteration Count Information::Reference CG iterations per set=50
# Iteration Count Information::Optimized CG iterations per set=50
# Iteration Count Information::Total number of reference iterations=5750
# Iteration Count Information::Total number of optimized iterations=5750
# ########## Reproducibility Summary  ##########=
# Reproducibility Information=
# Reproducibility Information::Result=PASSED
# Reproducibility Information::Scaled residual mean=3.08744e-07
# Reproducibility Information::Scaled residual variance=0
# ########## Performance Summary (times in sec) ##########=
# Benchmark Time Summary=
# Benchmark Time Summary::Optimization phase=0.0286376
# Benchmark Time Summary::DDOT=1.64479
# Benchmark Time Summary::WAXPBY=2.2919
# Benchmark Time Summary::SpMV=10.5722
# Benchmark Time Summary::MG=45.9738
# Benchmark Time Summary::Total=60.4858
# Floating Point Operations Summary=
# Floating Point Operations Summary::Raw DDOT=7.28341e+10
# Floating Point Operations Summary::Raw WAXPBY=7.28341e+10
# Floating Point Operations Summary::Raw SpMV=6.53865e+11
# Floating Point Operations Summary::Raw MG=3.64961e+12
# Floating Point Operations Summary::Total=4.44914e+12
# Floating Point Operations Summary::Total with convergence overhead=4.44914e+12
# GB/s Summary=
# GB/s Summary::Raw Read B/W=453.245
# GB/s Summary::Raw Write B/W=104.748
# GB/s Summary::Raw Total B/W=557.993
# GB/s Summary::Total with convergence and optimization phase overhead=552.88
# GFLOP/s Summary=
# GFLOP/s Summary::Raw DDOT=44.2817
# GFLOP/s Summary::Raw WAXPBY=31.7789
# GFLOP/s Summary::Raw SpMV=61.8478
# GFLOP/s Summary::Raw MG=79.3846
# GFLOP/s Summary::Raw Total=73.5568
# GFLOP/s Summary::Total with convergence overhead=73.5568
# GFLOP/s Summary::Total with convergence and optimization phase overhead=72.8829
# User Optimization Overheads=
# User Optimization Overheads::Optimization phase time (sec)=0.0286376
# User Optimization Overheads::Optimization phase time vs reference SpMV+MG time=0.0875411
# DDOT Timing Variations=
# DDOT Timing Variations::Min DDOT MPI_Allreduce time=0.0018699
# DDOT Timing Variations::Max DDOT MPI_Allreduce time=0.0018699
# DDOT Timing Variations::Avg DDOT MPI_Allreduce time=0.0018699
# Final Summary=
# Final Summary::HPCG result is VALID with a GFLOP/s rating of=72.8829
# Final Summary::HPCG 2.4 rating for historical reasons is=73.1585
# Final Summary::Results are valid but execution time (sec) is=60.4858
# Final Summary::Official results execution time (sec) must be at least=180