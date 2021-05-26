from abc import ABC, abstractmethod
import logging

import helpers


class Metric(ABC):
    @abstractmethod
    def __init__(self):
        self._events_of_interest = [helpers.SimulationEvent.BEGIN_SCENARIO]
        self.name = "Default Metric Class Name"

    @property
    def events_of_interest(self):
        return self._events_of_interest

    def add_event_of_interest(self, event):
        self._events_of_interest.append(event)

    def notify(self, event, **data):
        self.calculate()
        #TODO: prepare new scenario or calculate accordingly

    @abstractmethod
    def calculate(self):
        pass
    
    def export(self, target_dir):
        raise NotImplementedError #TODO

    @abstractmethod
    def draw(self, target_dir):
        pass




class AvgAccuracyPerRound(Metric):
    def __init__(self):
        super().__init__()
        self.add_event_of_interest(helpers.SimulationEvent.END_OF_ROUND)
        self.name = "Average Accuracy Per Rounds"

    def calculate(self):
        logging.debug("AvgAccuracyPerRound was called")

    def draw(self, target_dir):
        pass

class AvgAccuracyPerScenario(Metric):
    def __init__(self):
        super().__init__()
        self.add_event_of_interest(helpers.SimulationEvent.END_OF_SCENARIO)
        self.name = "Average Accuracy Per Scenarios"
    
    def calculate(self):
        logging.debug("AvgAccuracyPerScenario was called")

    def draw(self, target_dir):
        pass

class AvgAccuracyPerRound_Another(Metric):
    def __init__(self):
        super().__init__()
        self.add_event_of_interest(helpers.SimulationEvent.END_OF_ROUND)
    
    def calculate(self):
        logging.debug("AvgAccuracyPerRound_Another was called")

    def draw(self, target_dir):
        pass

class MetricBothRoundAndScenario(Metric):
    def __init__(self):
        super().__init__()
        self.add_event_of_interest(helpers.SimulationEvent.END_OF_SCENARIO)
        self.add_event_of_interest(helpers.SimulationEvent.END_OF_ROUND)
    
    def calculate(self):
        logging.debug("MetricBothRoundAndScenario was called")

    def draw(self, target_dir):
        pass