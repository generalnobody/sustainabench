from sustainabench.indicators import INDICATORS

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

    def process(self, raw_results, indicator_cfg):
        computed = {
            "workload": raw_results["workload"],
            "node_results": [],
            "metadata": raw_results["metadata"]
        }
        for node in raw_results["node_results"]:
            node_res = {} # Contains per-run derived metrics
            node_metadata = node["metadata"]
            for run in node["metrics"]:
                run_res = {}
                run_metrics = node["metrics"][run]
                for ind in self.indicators:
                    run_res.update(ind.compute(run_metrics, node_metadata, indicator_cfg))
                node_res.update({run: run_res})
            computed["node_results"].append({
                "node_id": node["node_id"],
                "metrics": node_res,
                "metadata": node_metadata
            })
            
        return computed

