import logging

import pyrepsys.helpers as helpers
import pyrepsys.metrics as metrics

logger = logging.getLogger(helpers.APP_NAME + "." + __name__)

class ResultsProcessor:
    def __init__(self, artifacts_directory):
        self.artifacts_directory = artifacts_directory
        self.metric_instances = {}
        self.active_metrics_by_events = {}
        for event in helpers.SimulationEvent:
            self.active_metrics_by_events[event] = set()

    def activate_metric(self, metric_classname):
        if metric_classname in self.metric_instances:
            metric = self.metric_instances[metric_classname]
            logger.debug("Found existing metric '{}'".format(metric))
        else:
            metric = getattr(metrics,metric_classname)()
            self.metric_instances[metric_classname] = metric
            logger.debug("Created metric '{}'".format(metric))

        for event in metric.events_of_interest:
            self.active_metrics_by_events[event].add(metric)

    def deactivate_all_metrics(self):
        for set_of_metrics in self.active_metrics_by_events.values():
            set_of_metrics.clear()

    def process(self, call_event, **event_details):
        """
        do the calculation for all active metrics
        'event_details' holds data for: 'agents_data' 'round_number' or 'scenario'
        """
        if call_event is helpers.SimulationEvent.BEGIN_SCENARIO:
            logger.debug("BEGIN_SCENARIO: {}".format(event_details["scenario"]))
        elif call_event is helpers.SimulationEvent.END_OF_ROUND:
            logger.debug("END_OF_ROUND: {}".format(event_details["round_number"]))
        elif call_event is helpers.SimulationEvent.END_OF_SCENARIO:
            logger.debug("END_OF_SCENARIO: {}".format(event_details["scenario"]))
        elif call_event is helpers.SimulationEvent.END_OF_SIMULATION:
            logger.debug("END_OF_SIMULATION")
        else:
            raise NotImplementedError #TODO

        if call_event is helpers.SimulationEvent.END_OF_SIMULATION:
            self.draw_all_metrics()
        else:
            for metric in self.active_metrics_by_events[call_event]:
                metric.notify(call_event, **event_details)

    def export_all_metrics(self):
        raise NotImplementedError #TODO

    def draw_all_metrics(self):
        for metric in self.metric_instances.values():
            metric.draw(self.artifacts_directory)