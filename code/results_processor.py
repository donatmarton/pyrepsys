import logging

import helpers


class ResultsProcessor:
    def __init__(self, artifacts_directory):
        self.artifacts_directory = artifacts_directory
        self.metrics_by_events = {}
        for event in helpers.SimulationEvent:
            self.metrics_by_events[event] = set()

    def attach_metric(self, metric):
        for event in metric.events_of_interest:
            self.metrics_by_events[event].add(metric)

    def detach_all_metrics(self):
        for set in self.metrics_by_events.values():
            set.clear()

    def process(self, call_event, **event_details):
        """
        do the calculation for all active metrics
        'event_details' holds data for: 'agents_data' 'round_number' or 'scenario'
        """
        if call_event is helpers.SimulationEvent.BEGIN_SCENARIO:
            logging.debug("BEGIN_SCENARIO: {}".format(event_details["scenario"]))
        elif call_event is helpers.SimulationEvent.END_OF_ROUND:
            logging.debug("END_OF_ROUND: {}".format(event_details["round_number"]))
        elif call_event is helpers.SimulationEvent.END_OF_SCENARIO:
            logging.debug("END_OF_SCENARIO: {}".format(event_details["scenario"]))
        else:
            raise NotImplementedError #TODO

        for metric in self.metrics_by_events[call_event]:
                metric.notify(call_event, **event_details)

    def export(self):
        raise NotImplementedError #TODO

    def draw(self):
        raise NotImplementedError #TODO