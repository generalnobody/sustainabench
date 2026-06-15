from sustainabench.measurement.base import InternalMeasurement, register_measurement
from pypapi import papi_low as papi
from pypapi import events
from pydantic import BaseModel

@register_measurement
class PapiMeasurement(InternalMeasurement):
    name = "papi"
    poll_interval = None
    
    require_file = True

    class MeasurementParams(BaseModel):
        events: list[str]

    def start(self):
        if not self.config:
            raise RuntimeError("Failed to start PyPAPI measurement as no config was provided")
        cfg = self.MeasurementParams.model_validate(self.config.measurement.params)

        papi.library_init()

        self.event_set = papi.create_eventset()
        self.active_events = []

        for name in cfg.events:
            ev = getattr(events, name, None)

            if not ev:
                print(f"PyPAPI: Unknown event: {name}")
                continue

            try:
                papi.add_event(self.event_set, ev)
                self.active_events.append(name)
            except Exception as e:
                print(f"Could not add {name}: {e}")

        papi.start(self.event_set)

    def sample(self):
        pass

    def stop(self):
        self.papi_values = papi.stop(self.event_set)

    def result(self):
        return {
            f"{self.name}": dict(zip(self.active_events, self.papi_values))
        }