# SustainaBench
A sustainability benchmarking framework.

## Install

To install, first clone this repository using `git clone`. Then, enter the cloned directory.

Please ensure that the correct command is used for the PyTorch wheel. For CUDA GPUs (NVIDIA), run (default index URL fetches torch for CUDA):

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

If you wish to add custom modules and avoid needing to reinstall the framework each time, install using the `-e` flag:

```bash
pip install -e .
```

## Run

To run the framework, use the `sustainabench` command. The following subcommands are available (use the `--help` menu when running each command to get additional information):

```bash
sustainabench run benchmark <options>       # Runs the benchmark
sustainabench run benchmark-list <options>  # Lists available benchmarking options
```

To calculate the metrics, run:

```bash
sustainabench result generate <options>     # Generates results based on input file
```

If multiple separate benchmark runs need to be merged (for instance because the benchmark was conducted more after the initial number of runs), run:

```bash
sustainabench result merge <options>        # Merges benchmark results
```

Please note: This benchmark suite assumes exclusive access to the node that the benchmark is run on. Otherwise, actions performed by other users may impact the final results.

### Scripts

For the experiments conducted to evaluate this project, the scripts are located in the `scripts/` folder. Specifically, the scripts under the `scripts/snellius/` directory were used for the evaluation, while the scripts under the `scripts/das6/` folder were used to test the project on the VU DAS6 cluster before final execution on the Dutch national supercomputer, Snellius.

## Expand

It is possible to add new workloads, measurement modules, metrics and execution backends to extend the framework.

### Workloads

To add additional workloads, add them to the `sustainabench/workloads` folder. Each workload should extend the base `InternalWorkload` or `ExternalWorkload` class defined in `sustainabench/workloads/base.py`, depending on whether implementing an internal or external workload:

```python
class Workload(ABC):
    """Base class for all benchmark workloads."""
    # Every workload must define this
    name: str
    require_config: bool = False

class InternalWorkload(Workload):
    "Handles internal workloads (workloads without their own metrics)."
    @abstractmethod
    def run(self, num_processors: int, context=None):
        """Execute workload."""
        pass

class ExternalWorkload(Workload):
    """Handles external workloads (workloads with their own metrics)."""    

    require_wrapping: bool = False

    @abstractmethod
    def execute(self):
        # Execute the external workload. Expected to be something like running a command-line subprocess
        pass

    @abstractmethod
    def process(self, backend_name: str) -> dict[str, Any]:
        # Process the results obtained from the execute() method. Please make sure to turn them into a format that fits what this suite expects.
        pass
```

The base `Workload` class contains data universal across workloads. The `name` parameter defined the workload's name, used when running the workload; the `require_config` boolean defines whether the workload requires a separate file to configure workload-specific parameters. If it does, this is set to the `workload_cfg` parameter of the `Workload` class.

The `InternalWorkload` class allows for implementing internal workloads. These are ones that generally do not have their own metrics, just designed to stress the system and leave measurement to the other measurements. This class only has the `run()` function that is called to execute the workload.

The `ExternalWorkload` class allows for implementing external workloads, ones that generally provide their own metrics or are separate programs that cannot be called as internal workloads. This class has the `require_wrapping` boolean that defines whether the workload requires being run by a wrapper such as MPI (the specific wrapper cannot be defined as there are a lot of possibilities with some workloads, such as for MPI it would work with _mpirun_, _likwid-mpirun_, _srun_, etc.; this requires manually ensuring the correct backend/measurement is selected). The class has two functions - `execute()` and `process()`. The `execute()` function executes the workload (ensuring itself that output of execution is stored correctly), while the `process()` function takes the executed workload's output and processes it to obtain any metrics that are required, returning it in the universal format. 

### Measurements

To add additional measurements, similar to adding additional workloads, add a new Python file with the desired logic to `sustainabench/measurement`. Each measurement should extend the base `InternalMeasurement` or `ExternalMeasurement` class defined in `sustainabench/measurement/base.py`, depending on whether writing an internal or external measurement:

```python
class Measurement(ABC):
    """Base Measurement class"""
    name: str
    require_file: bool # Control whether this metric should require a file path to be included or not.
    config: MeasurementConfig | None = None
    only_once_per_node: bool = False # Only execute this measurement once per node. Especially useful for energy measurements in MPI situations, to prevent duplicate measurements.

class InternalMeasurement(Measurement):
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

class ExternalMeasurement(Measurement):
    # The higher the rank priority, if multiple external measurements are to be conducted, the earlier this one gets started. 
    # Is superceded by wrapper priority though, where, if external measurement can act as a backend wrapper replacement, it will, regardless of this priority, following wrapper priority.
    rank_priority: int = 0 
    wrapper_priority: int = 0 # External measurement with highest wrapper priority that is compatible with a certain backend will be the one to be selected as the replacement wrapper
    within_wrapper: bool = False # Whether this measurement should be run within the wrapper. Like, for MPI, if this should be run for each rank.
    replace_wrapper: list[str] = [] # List of backends for which this can replace the wrapper functionality (e.g. likwid-mpirun instead of mpirun, for likwid measurement)
    wrapper_conflicts: list[str] = [] # List of other external measurement names that this measurement conflicts with
    
    @abstractmethod
    def get_wrap_command(self, backend_name, node_processors) -> list[str]:
        pass

    @abstractmethod
    def process_results(self, output: str, nodeids: list[str]) -> dict:
        pass

```

The base `Measurement` class contains some universal data that can be defined for each measurement, such as its name, whether the measurement requires any files, a configuration, and whether the measurement should only be executed once per node, regardless of whether multiple ranks, such as with MPI, are present.

The `InternalMeasurement` class is responsible for internal measurements. These are measurements that can be executed in parallel to the main workload in a separate thread. Here, `poll_interval` is defined if the measurement should measure over time, polling every `<poll_interval>` seconds. The `sample()` function is only called if `poll_interval` is set. The `start()` function is called when setting the measurement up and to perform the first measurement. The `stop()` function stops the measurement and cleans up whatever is required. The `result()` function processes the measurements obtained during the measurement's process and is called after `stop()`.

The `ExternalMeasurement` class is responsible for external measurements. These are ones that generally require wrap-around execution, such as _likwid_ and _perf_. This class' parameters are explained in the corresponding comments. The `get_wrap_command()` function retrieves the command with which to perform wrap-around execution, while the `process_results` function parses the raw output data into the common schema used in this project.

### Metrics

Additional metrics are added similarly to the other two aspects, by adding a new Python file with the desired logic to `sustainabench/metrics`. Each metric should extend the base `Metric` class defined in `sustainabench/metrics/base.py`:

```python
class Metric(ABC):
    """Base Metric class"""
    name: str
    require_file: bool                  # Control whether this metric should require a file path to be included or not.
    required_metrics: list[str] = []    # Which DERIVED metrics to require. Makes this happen after those are computed (e.g. performance-per-carbon requires carbon).

    @abstractmethod
    def __init__(self, filename: str, metrics_dict: MetricsDict) -> None:
        pass

    @abstractmethod
    def setup(self, metric_config: MetricConfig | None) -> None:
        pass

    @abstractmethod
    def compute(self, node_id: str, measurements: dict, metadata: dict, run_metrics: list[NodeResult], node_results: list[NodeResult]) -> dict:
        pass
```

The `__init__()` function is executed on metric initialisation and allows for passing required files as `filename`, while the `metrics_dict` is the dictionary representing the paths to metrics and how metrics should be handled among each other (summation, priorities, etc.).

The `setup()` function is responsible for initial setup of the metric. The `metric_config` represents whether the metric requires a specific configuration to function. Not required.

The `compute()` function is executed to calculate the metric. Its parameters are passed by the calling function, with `node_id`, `measurements` and `metadata` being fields from the current node's results, the `run_metrics` containing all node's results in case required, and `node_results` containing all already generated results with new metrics if required (usually used when `required_metrics` is used).

### Backends

Additional execution backends can be added by adding a new Python file with the desired logic to `sustainabench/core/backends/`. Each backend should extend the base `ExecutionBackend` class defined in `sustainabench/core/backends/base.py`:

```python
class ExecutionBackend(ABC):
    """Defines how workloads are executed."""
    name: str

    @abstractmethod
    def run(self, runner) -> list[NodeResult]:
        pass

    @abstractmethod
    def get_wrap_command(self) -> list[str]:
        pass
```

The `get_wrap_command()` function can be overridden to define whether the backend requires command wrapping of the workload (like with MPI's `mpirun`).

The `run()` function is responsible for handling the execution of the workload.

## Configuration

This project uses Pydantic schemas to handle all configuration. This ensures (at least part of) the input files match expected formats and simplifies error handling.

The universal schemas can be found in the `sustainabench/schemas/configs/` folder. Here, the files define the base formats expected for the measurement, metrics and workloads configurations. However, this only handles the basic configuration formats. After that, specific formats need to be handled individually within each measurement, metric or workload to properly utilise the provided configs. It is recommended to write your own Pydantic schemas for those sub-parts within each individual extended module, ensuring that the configurations match. There are annotated examples for workload, metrics and measurement configurations in the `configs/` folder. Refer to those to see how they can be defined.

When performing metric derivation, one of the provided configuration files is the metrics dictionary. This is a YAML file that defines where each metric is located for a specific unit, allowing for multiple paths, and allowing for defining some limited behaviour for each path. Do keep in mind that specific behaviour has to be explicitly defined in each metric and has not been made universal so far.

Simplified, the metrics dictionary allows for two types of metrics, one that is a `scalar`, indicating that the listed path only leads to a single value, while the other is a `collection`, where the path leads to multiple values. A `scalar` metric has three additional parameters - the path (from the global metric name), whether the value contributes to a total if that is relevant to the metric (true or false) and a contribution group (if interested in getting separate data for separate components, such as CPU and GPU specific data; can be defined manually). A `collection` metric has more additional parameters: the `collection_path`, which points to the item from where the collection may take multiple routes to reach the desired values, the `value_path`, which shows how to traverse the object tree from the object pointed to by the `collection_path` down to the desired value, the `label_path`, an optional value that can be defined if you wish to have specific ID's for each of the values, and, like the `scalar` metric, the `contributes_to_total` and `contribution_group` parameters which work the same. Keep in mind that all paths use JMESPath, so use that formatting for path definition. 

The metrics dict is structured as follows:

```yaml
metrics_dict:
  - unit: <unit_name> # List of these unit objects. Can be as many as needed.
    sources:
      <metric_name>: # Name of the metric. Either a measurement name or can also be a metric name for a prior-calculated metric. Used as the first name to select an object from all the results.
        priority: 0 # Higher priority means that this metric will be prioritised when calculating a total over others. Higher priority overrides lower priority, equal priority sums values.
        metrics:
          - kind: scalar
            path: <path_to_value> # Path to the value within the <metric_name> object.
            contributes_to_total: <true|false> # Whether to contribute to a calculated total or not
            contribution_group: <group_name|null> # A group to which this metric always contributes. e.g. separate CPU and GPU totals.

          - kind: collection
            collection_path: <path_to_collection_object> # Path to the object from where paths to values may diverge, within the <metric_name> object.
            value_path: <path_to_value> # Path to the value from each object within the <collection_path> object(s)
            label_path: <path_to_label> # Path to the ID for each found value from within the <collection_path> object(s)
            contributes_to_total: <true|false> # Same as with scalar
            contribution_group: <group_name|null> # Same as with scalar
```
