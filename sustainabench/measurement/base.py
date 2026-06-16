from abc import ABC, abstractmethod
from typing import Dict, Type
import yaml
from sustainabench.schemas.configs.measurement import MeasurementConfig

MEASUREMENTS: Dict[str, Type["Measurement"]] = {}

def register_measurement(cls):
    """Macro used by each measurement to register in MEASUREMENTS"""
    MEASUREMENTS[cls.name] = cls
    return cls


class Measurement(ABC):
    """Base Measurement class"""
    name: str
    require_file: bool # Control whether this metric should require a file path to be included or not.
    config: MeasurementConfig | None = None
    filename: str | None = None
    only_once_per_node: bool = False # Only execute this measurement once per node. Especially useful for energy measurements in MPI situations, to prevent duplicate measurements.

    def __init__(self, filename: str) -> None:
        self.filename = filename
        if filename is not None and filename != "":
            cfg = None
            with open(filename) as f:
                cfg = yaml.safe_load(f)
            self.config = MeasurementConfig.model_validate(cfg)
            if self.config.measurement.name != self.name:
                raise ValueError(f"Config's name '{self.config.measurement.name}' does not match measurement's name: '{self.name}'")
    

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
