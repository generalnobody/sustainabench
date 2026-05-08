from sustainabench.indicators import INDICATORS
from sustainabench.schemas.results.benchmark import BenchmarkResult, NodeResult
from sustainabench.schemas.configs.indicators.config import IndicatorConfig

class ResultProcessor:
    """Class than handles processing raw results"""

    def __init__(self, indicator_names):
        indicator_dict = {}
        for name in indicator_names:
            file = ""
            if "=" in name:
                name, file = name.split("=", 1)
            if name not in INDICATORS:
                raise ValueError(f"Unknown indicator: {name}")
            indicator_dict[name] = file

        self.indicators = [
            INDICATORS[name](file)
            for name, file in indicator_dict.items()
        ]

        for indicator in self.indicators: # Check if all indicators got their required files
            if indicator.require_file and indicator_dict[indicator.name] == "":
                raise ValueError(f"File not provided for indicator '{indicator.name}'. Use as follows: -i {indicator.name}=<file>.")
            
    def get_loaded_indicators(self):
        return [
            ind.name
            for ind in self.indicators
        ]

    def process(self, raw_results: BenchmarkResult, indicator_cfg: IndicatorConfig | None) -> BenchmarkResult:
        results: dict[str, list[NodeResult]] = {}

        for ind in self.indicators: # Setup all indicators. Prevents needing to re-config for every node for every run
            ind.setup(indicator_cfg)
            
        for run, node_results in raw_results.results.items():
            run_results = []
            for node_result in node_results:
                node_metrics = {}
                for ind in self.indicators:
                    node_metrics.update(ind.compute(node_result.metrics, node_result.metadata))
                run_results.append(NodeResult(node_id=node_result.node_id, metrics=node_metrics, metadata=node_result.metadata))
            results.update({run: run_results})

        return BenchmarkResult(
            workload=raw_results.workload, 
            backend=raw_results.backend, 
            results=results, 
            metadata=raw_results.metadata
        )


