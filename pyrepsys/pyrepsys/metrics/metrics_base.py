from abc import ABC, abstractmethod

from pyrepsys.helper_types import SimulationEvent


class Metric(ABC):
    @abstractmethod
    def __init__(self):
        self._events_of_interest = []
        self.add_event_of_interest(SimulationEvent.BEGIN_SCENARIO)
        self.name = "Default Metric Class Name"

    @property
    def events_of_interest(self):
        return self._events_of_interest

    def add_event_of_interest(self, event):
        self._events_of_interest.append(event)

    def notify(self, event, **data):
        if event is SimulationEvent.BEGIN_SCENARIO:
            self.prepare_new_scenario(data["scenario"])
        else:
            self.calculate(**data)

    @abstractmethod
    def prepare_new_scenario(self, scenario):
        pass

    @abstractmethod
    def calculate(self, **data):
        pass
    
    def export(self, target_dir):
        raise NotImplementedError #TODO

    @abstractmethod
    def draw(self, target_dir):
        pass


class ScenarioDataPoints:
    def __init__(self, scenario_name):
        self.name = scenario_name
        self.x = []
        self.y = []

    def record_data_point(self, x, y):
        self.x.append( x )
        self.y.append( y )


"""
# Example stub metric to help creating new ones

class MetricNameHere(Metric):
    def __init__(self):
        super().__init__()
        # TODO: add events of interest
        self.add_event_of_interest(SimulationEvent.END_OF_ROUND)
        self.add_event_of_interest(SimulationEvent.END_OF_SCENARIO)
        # TODO: change name of metric
        self.name = "Average Accuracy Per Scenarios"
    
    def prepare_new_scenario(self, scenario):
        # TODO: implement method, called before simulating a scenario
        logger.debug("MetricNameHere scenario preparation: {}".format(scenario))

    def calculate(self, **data):
        # TODO: implement method called on added events of interest
        logger.debug("MetricNameHere was called")

    def draw(self, target_dir):
        # TODO: implement method to draw and saves the metric
        logger.debug("MetricNameHere draw")

"""