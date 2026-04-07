from sustainabench.indicators import INDICATORS

class ResultProcessor:
    """Class than handles processing raw results"""

    def __init__(self, raw_results, indicator_names):
        for name in indicator_names:
            if name not in INDICATORS:
                raise ValueError(f"Unknown indicator: {name}")
            
        self.indicators = [
            INDICATORS[name]()
            for name in indicator_names
        ]

        self.raw_results = raw_results

    def process(self, ):
        computed = {}
        for ind in self.indicators:
            computed.update(ind.compute(self.raw_results))

        return computed

