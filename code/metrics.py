from abc import ABC, abstractmethod
import logging
import os

from matplotlib import pyplot as plt

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
        if event is helpers.SimulationEvent.BEGIN_SCENARIO:
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


class ScenarioDataByRounds:
    def __init__(self, scenario_name):
        self.name = scenario_name
        self.round_indices = []
        self.round_data = []

    def record_round(self, round_index, round_data):
        self.round_indices.append(round_index)
        self.round_data.append(round_data)

class AvgAccuracyPerRound(Metric):
    def __init__(self):
        super().__init__()
        self.add_event_of_interest(helpers.SimulationEvent.END_OF_ROUND)
        self.name = "Average Accuracy Per Rounds"
        self.scenarios_data = []

    def prepare_new_scenario(self, scenario):
        logging.debug("AvgAccuracyPerRound scenario preparation: {}".format(scenario))
        self.scenarios_data.append( ScenarioDataByRounds(scenario) )

    def calculate(self, **data):
        logging.debug("AvgAccuracyPerRound was called")
        agents_data = data["agents_data"]
        round_number = data["round_number"]

        avg_accuracy = round_number

        self.scenarios_data[-1].record_round(round_number, avg_accuracy)

    def draw(self, target_dir):
        logging.debug("AvgAccuracyPerRound draw to {}".format(target_dir))
        fig, ax = plt.subplots()  # Create a figure containing a single axes.
        ax.set_title(self.name)
        ax.set_xlabel("Round")
        ax.set_ylabel("Average accuracy")

        for scenario in self.scenarios_data:
            ax.plot(
                scenario.round_indices,
                scenario.round_data,
                'o',
                label=scenario.name)

        ax.legend()
        ax.grid()
        
        figfile = os.path.join(target_dir,type(self).__name__)
        fig.savefig(figfile)

class AvgAccuracyPerScenario(Metric):
    def __init__(self):
        super().__init__()
        self.add_event_of_interest(helpers.SimulationEvent.END_OF_SCENARIO)
        self.name = "Average Accuracy Per Scenarios"
    
    def prepare_new_scenario(self, scenario):
        logging.debug("AvgAccuracyPerScenario scenario preparation: {}".format(scenario))

    def calculate(self, **data):
        logging.debug("AvgAccuracyPerScenario was called")

    def draw(self, target_dir):
        logging.debug("AvgAccuracyPerScenario draw")

class AvgAccuracyPerRound_Another(Metric):
    def __init__(self):
        super().__init__()
        self.add_event_of_interest(helpers.SimulationEvent.END_OF_ROUND)
    
    def prepare_new_scenario(self, scenario):
        logging.debug("AvgAccuracyPerRound_Another scenario preparation: {}".format(scenario))

    def calculate(self, **data):
        logging.debug("AvgAccuracyPerRound_Another was called")

    def draw(self, target_dir):
        logging.debug("AvgAccuracyPerRound_Another draw")

class MetricBothRoundAndScenario(Metric):
    def __init__(self):
        super().__init__()
        self.add_event_of_interest(helpers.SimulationEvent.END_OF_SCENARIO)
        self.add_event_of_interest(helpers.SimulationEvent.END_OF_ROUND)
    
    def prepare_new_scenario(self, scenario):
        logging.debug("MetricBothRoundAndScenario scenario preparation: {}".format(scenario))

    def calculate(self, **data):
        logging.debug("MetricBothRoundAndScenario was called")

    def draw(self, target_dir):
        logging.debug("MetricBothRoundAndScenario draw")