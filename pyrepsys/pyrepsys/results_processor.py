import logging

from pyrepsys.helper_types import SimulationEvent
from pyrepsys.errors import UncompleteInitializationError

logger = logging.getLogger(__name__)

class ResultsProcessor:
    def __init__(self, artifacts_directory):
        self.artifacts_directory = artifacts_directory
        self.metric_instances = {}
        self.active_metrics_by_events = {}
        for event in SimulationEvent:
            self.active_metrics_by_events[event] = set()

    def activate_metric(self, metric_classname):
        try:
            metric = self.metric_instances[metric_classname]
            for event in metric.events_of_interest:
                self.active_metrics_by_events[event].add(metric)
            logger.debug("Activated existing metric '{}'".format(metric))
        except KeyError:
            raise UncompleteInitializationError("tried activating metric '{}' but I (reproc) don't have it".format(metric_classname))

    def deactivate_all_metrics(self):
        for set_of_metrics in self.active_metrics_by_events.values():
            set_of_metrics.clear()

    def has_metric(self, metric_classname):
        return metric_classname in self.metric_instances

    def add_metric(self, metric_object):
        self.metric_instances[type(metric_object).__name__] = metric_object
        logger.debug("Added metric '{}'".format(metric_object))

    def process(self, call_event, **event_details):
        """
        do the calculation for all active metrics
        'event_details' holds data for: 'agents_data' 'round_number' or 'scenario'
        """
        if call_event is SimulationEvent.BEGIN_SCENARIO:
            logger.debug("BEGIN_SCENARIO: {}".format(event_details["scenario"]))
        elif call_event is SimulationEvent.END_OF_ROUND:
            logger.debug("END_OF_ROUND: {}".format(event_details["round_number"]))
        elif call_event is SimulationEvent.END_OF_SCENARIO:
            logger.debug("END_OF_SCENARIO: {}".format(event_details["scenario"]))
        elif call_event is SimulationEvent.END_OF_SIMULATION:
            logger.debug("END_OF_SIMULATION")
        else:
            raise NotImplementedError #TODO

        if call_event is SimulationEvent.END_OF_SIMULATION:
            logger.info("Started drawing & exporting metrics")
            self.export_all_metrics()
        else:
            for metric in self.active_metrics_by_events[call_event]:
                metric.notify(call_event, **event_details)

    def export_all_metrics(self):
        for metric in self.metric_instances.values():
            metric.export(self.artifacts_directory)