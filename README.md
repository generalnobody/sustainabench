# SustainaBench
A sustainability benchmarking tool.

## Install

To install, first clone this repository using `git clone`. Then, enter the cloned directory.

Please ensure correct install for GPU version. For CUDA GPUs (NVIDIA), run (default index URL fetches torch for CUDA):

```bash
pip install . 
```

For CUDA 12.6 (used during development):
```bash
pip install . --extra-index-url https://download.pytorch.org/whl/cu126
```

For ROCm GPUs (AMD), run:
```bash
pip install . --extra-index-url https://download.pytorch.org/whl/rocm7.2
```

When neither is available (CPU-only), run:
```bash
pip install . --extra-index-url https://download.pytorch.org/whl/cpu
```

If you wish to add custom modules, install using the `-e` flag:

```bash
pip install -e .
```

## Run

To run the tool, in the project directory, use the `sustainabench` command. The following subcommands are available (use the `--help` menu when running each command to get additional information):

```bash
sustainabench run benchmark <options>       # Runs the benchmark
sustainabench run benchmark-list <options>  # Lists available benchmarking options
```

To calculate the metrics, run:

```bash
sustainabench result generate <options>     # Generates results based on input file
```

Please note: This benchmark suite assumes exclusive access to the node that the benchmark is run on. Otherwise, actions performed by other users may impact the final results.

## Expand

To expand this project with additional modules, please ensure the project was installed in the editable configuration. It is possible to add new workloads, new measurement modules and additional metrics.

### Workloads

To add additional workloads, add them to the `sustainabench/workloads` folder. Each workload should extend the base `Workload` class defined in `sustainabench/workloads/base.py`:

```python
class Workload(ABC):
    """Base class for all benchmark workloads."""

    # Every workload must define this
    name: str

    @abstractmethod
    def run(self, *args: object, **kwargs: object):
        """Execute workload."""
        pass
```

### Measurements

To add additional measurements, similar to adding additional workloads, add a new Python file with the desired logic to `sustainabench/measurement`. Each measurement should extend the base `Measurement` class defined in `sustainabench/measurement/base.py`:

```python
class Measurement(ABC):
    """Base Measurement class"""
    name: str
    poll_interval: float | None = None # Seconds

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def sample(self):
        "Called repeatedly if poll_interval is set"
        pass

    @abstractmethod
    def result(self) -> dict:
        pass
```

Here, `poll_interval` is defined if the measurement should measure over time, polling every `<poll_interval>` seconds. The `sample` function is only called if `poll_interval` is set. 

### Metrics

Additional metrics are added similarly to the other two aspects, by adding a new Python file with the desired logic to `sustainabench/metrics`. Each metric should extend the base `Metric` class defined in `sustainabench/metrics/base.py`:

```python
class Metric(ABC):
    """Base Metric class"""
    name: str

    @abstractmethod
    def compute(self, measurements: dict) -> dict:
        pass
```
