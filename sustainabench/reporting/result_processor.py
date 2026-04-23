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
        computed = {}
        for ind in self.indicators:
            computed.update(ind.compute(raw_results, indicator_cfg))

        return computed

