from abc import ABC, abstractmethod
from typing import Dict, Type
import yaml
from sustainabench.schemas.configs.measurement.config import MeasurementConfig

MEASUREMENTS: Dict[str, Type["Measurement"]] = {}

def register_measurement(cls):
    """Macro used by each measurement to register in MEASUREMENTS"""
    MEASUREMENTS[cls.name] = cls
    return cls


class Measurement(ABC):
    """Base Measurement class"""
    name: str
    poll_interval: float | None = None # Seconds
    scope: str
    require_file: bool # Control whether this indicator should require a file path to be included or not.
    config: MeasurementConfig | None = None

    def __init__(self, filename: str) -> None:
        if filename != "":
            cfg = None
            with open(filename) as f:
                cfg = yaml.safe_load(f)
            self.config = MeasurementConfig.model_validate(cfg)
            if self.config.measurement.name != self.name:
                raise ValueError(f"Config's name '{self.config.measurement.name}' does not match measurement's name: '{self.name}'")

    @abstractmethod
    def is_external(self) -> bool:
        pass
    

class InternalMeasurement(Measurement):
    def is_external(self) -> bool:
        return False

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
    priority: int = 0
    # The higher the priority, if multiple external measurements are to be conducted, the earlier this one gets started
    def is_external(self) -> bool:
        return True
    
    @abstractmethod
    def execute_cli_passthrough(self, workload, measurements, runs, config_file, backend, node_processors, processors, output_dir, output_filename):
        pass

    @abstractmethod
    def result_json(self, nodeids: list[str]) -> dict:
        pass
