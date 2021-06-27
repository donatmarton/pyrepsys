import logging

from .metrics_base import Metric
from pyrepsys.helper_types import SimulationEvent


logger = logging.getLogger(__name__)

# these are example metrics used for testing, debugging

class AvgAccuracyPerRound_Another(Metric):
    def __init__(self):
        super().__init__()
        self.add_event_of_interest(SimulationEvent.END_OF_ROUND)
    
    def prepare_new_scenario(self, scenario):
        logger.debug("AvgAccuracyPerRound_Another scenario preparation: {}".format(scenario))

    def calculate(self, **data):
        logger.debug("AvgAccuracyPerRound_Another was called")

    def draw(self, target_dir):
        logger.debug("AvgAccuracyPerRound_Another draw")

class MetricBothRoundAndScenario(Metric):
    def __init__(self):
        super().__init__()
        self.add_event_of_interest(SimulationEvent.END_OF_SCENARIO)
        self.add_event_of_interest(SimulationEvent.END_OF_ROUND)
    
    def prepare_new_scenario(self, scenario):
        logger.debug("MetricBothRoundAndScenario scenario preparation: {}".format(scenario))

    def calculate(self, **data):
        logger.debug("MetricBothRoundAndScenario was called")

    def draw(self, target_dir):
        logger.debug("MetricBothRoundAndScenario draw")