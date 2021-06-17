from abc import ABC, abstractmethod
import logging
import os

from matplotlib import pyplot as plt

import pyrepsys.helpers as helpers
import pyrepsys.config as config

logger = logging.getLogger(__name__)

class Metric(ABC):
    @abstractmethod
    def __init__(self):
        self._events_of_interest = []
        self.add_event_of_interest(helpers.SimulationEvent.BEGIN_SCENARIO)
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

"""
# Example stub metric to help creating new ones

class MetricNameHere(Metric):
    def __init__(self):
        super().__init__()
        # TODO: add events of interest
        self.add_event_of_interest(helpers.SimulationEvent.END_OF_ROUND)
        self.add_event_of_interest(helpers.SimulationEvent.END_OF_SCENARIO)
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
        self.name = "Average Inaccuracy of Raters Per Rounds"
        self.scenarios_data = []

    def prepare_new_scenario(self, scenario):
        logger.debug("AvgAccuracyPerRound scenario preparation: {}".format(scenario))
        self.scenarios_data.append( ScenarioDataByRounds(scenario) )

    def calculate(self, **data):
        logger.debug("AvgAccuracyPerRound was called")
        agents_data = data["agents_data"]
        round_number = data["round_number"]

        #avg( | estimated - claim ground truth | ) for all claims of all agents
        agent_accuracies =  []
        for agent in agents_data:
            for claim in agent.claims:
                if len(claim.reviews) > 0:
                    review_scores = []
                    for review in claim.reviews:
                        review_scores.append(review.value)
                    review_avg = sum(review_scores) / len(review_scores)
                    accuracy = abs( claim.ground_truth - review_avg )
                    agent_accuracies.append(accuracy)
        avg_accuracy = sum(agent_accuracies) / len(agent_accuracies)

        self.scenarios_data[-1].record_round(round_number, avg_accuracy)

    def draw(self, target_dir):
        logger.debug("AvgAccuracyPerRound draw to {}".format(target_dir))
        fig, ax = plt.subplots()
        ax.set_title(self.name)
        ax.set_xlabel("Round")
        ax.set_ylabel("Average inaccuracy")

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
        logger.debug("AvgAccuracyPerScenario scenario preparation: {}".format(scenario))

    def calculate(self, **data):
        logger.debug("AvgAccuracyPerScenario was called")

    def draw(self, target_dir):
        logger.debug("AvgAccuracyPerScenario draw")

class ScenarioDataPoints:
    def __init__(self, scenario_name):
        self.name = scenario_name
        self.x = []
        self.y = []

    def record_data_point(self, x, y):
        self.x.append( x )
        self.y.append( y )

class AvgTotClaimInaccuracyAndReputationScatter(Metric):
    def __init__(self):
        super().__init__()
        self.add_event_of_interest(helpers.SimulationEvent.END_OF_SCENARIO)
        self.name = "Reputation vs Average Total Claiming Inaccuracy"
        self.scenarios_data = []

    def prepare_new_scenario(self, scenario):
        self.scenarios_data.append( ScenarioDataPoints(scenario) )

    def calculate(self, **data):
        agents_data = data["agents_data"]
        
        # reputation and total claiming honesty (= |gr.truth - claim value| )
        # idea is to show how good the reputation is in approximating "honesty"

        for agent in agents_data:
            # include agents with published claims only
            if len(agent.claims) > 0:
                tot_claim_honesties = []
                for claim in agent.claims:
                    tot_claim_honesties.append(abs( claim.ground_truth - claim.author_review.value ))
                avg_tot_claim_hon = sum(tot_claim_honesties) / len(tot_claim_honesties)

                rep = agent.global_reputation

                self.scenarios_data[-1].record_data_point(avg_tot_claim_hon, rep)

    def draw(self, target_dir):
        fig, ax = plt.subplots()
        
        min_rating = config.get("MIN_RATING")
        max_rating = config.get("MAX_RATING")
        min_reputation = min_rating
        max_reputation = max_rating
        
        for scenario in self.scenarios_data:
            ax.set_title("Scenario: " + scenario.name)
            
            ax.set_xlabel("Average Total Claiming Inaccuracy")
            ax.set_ylabel("Reputation")
            
            ax.set_xlim(0, max_rating - min_rating)
            ax.set_ylim(min_reputation, max_reputation)
            ax.grid()

            ax.scatter(scenario.x, scenario.y)
        
            figfile = os.path.join(target_dir, type(self).__name__ + "_" + scenario.name)
            fig.savefig(figfile)
            
            ax.clear()




# these are example metrics used for testing, debugging:

class AvgAccuracyPerRound_Another(Metric):
    def __init__(self):
        super().__init__()
        self.add_event_of_interest(helpers.SimulationEvent.END_OF_ROUND)
    
    def prepare_new_scenario(self, scenario):
        logger.debug("AvgAccuracyPerRound_Another scenario preparation: {}".format(scenario))

    def calculate(self, **data):
        logger.debug("AvgAccuracyPerRound_Another was called")

    def draw(self, target_dir):
        logger.debug("AvgAccuracyPerRound_Another draw")

class MetricBothRoundAndScenario(Metric):
    def __init__(self):
        super().__init__()
        self.add_event_of_interest(helpers.SimulationEvent.END_OF_SCENARIO)
        self.add_event_of_interest(helpers.SimulationEvent.END_OF_ROUND)
    
    def prepare_new_scenario(self, scenario):
        logger.debug("MetricBothRoundAndScenario scenario preparation: {}".format(scenario))

    def calculate(self, **data):
        logger.debug("MetricBothRoundAndScenario was called")

    def draw(self, target_dir):
        logger.debug("MetricBothRoundAndScenario draw")