from abc import ABC, abstractmethod
import logging

import helpers


class Metric(ABC):
    name = "Default Metric Class"

    @property
    @abstractmethod
    def events_of_interest(self):
        pass

    @abstractmethod
    def calculate(self):
        pass
    
    def export(self, target_dir):
        raise NotImplementedError #TODO

    @abstractmethod
    def draw(self, target_dir):
        pass




class AvgAccuracyPerRound(Metric):
    @property
    def events_of_interest(self):
        return [helpers.SimulationEvent.END_OF_ROUND]

    def calculate(self):
        logging.debug("AvgAccuracyPerRound was called")

    def draw(self, target_dir):
        pass

class AvgAccuracyPerScenario(Metric):
    @property
    def events_of_interest(self):
        return [helpers.SimulationEvent.END_OF_SCENARIO]
    
    def calculate(self):
        logging.debug("AvgAccuracyPerScenario was called")

    def draw(self, target_dir):
        pass

class AvgAccuracyPerRound_Another(Metric):
    @property
    def events_of_interest(self):
        return [helpers.SimulationEvent.END_OF_ROUND]
    
    def calculate(self):
        logging.debug("AvgAccuracyPerRound_Another was called")

    def draw(self, target_dir):
        pass

class MetricBothRoundAndScenario(Metric):
    @property
    def events_of_interest(self):
        return [
            helpers.SimulationEvent.END_OF_SCENARIO,
            helpers.SimulationEvent.END_OF_ROUND]
    
    def calculate(self):
        logging.debug("MetricBothRoundAndScenario was called")

    def draw(self, target_dir):
        pass