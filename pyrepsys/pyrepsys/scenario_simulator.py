import random
import logging

import pyrepsys.config as config
from pyrepsys.agent import Agent
import pyrepsys.helpers as helpers

logger = logging.getLogger(__name__)

class ScenarioSimulator:

    def __init__(self, reputation_strategy=None):
        self._reputation_strategy = reputation_strategy
        self.agents = []
        self._improvement_handler = None
        self.rng = random.Random()
        self.results_processor = None

    @property
    def reputation_strategy(self):
        return self._reputation_strategy

    @reputation_strategy.setter
    def reputation_strategy(self, reputation_strategy):
        self._reputation_strategy = reputation_strategy
        logger.info("Reputation strategy set to '{}'".format(type(reputation_strategy).__name__))

    @property
    def improvement_handler(self):
        return self._improvement_handler

    @improvement_handler.setter
    def improvement_handler(self, improvement_handler):
        self._improvement_handler = improvement_handler
        logger.info("Improvement handler chain entry point set to '{}'".format(type(improvement_handler).__name__))

    def create_agents(self, distort_strategy, rate_strategy, claim_limits, claim_probability, rate_probability, claim_truth_assessment_inaccuracy, amount=1):
        for _ in range(0,amount):
            new_agent = Agent(distort_strategy, rate_strategy, claim_limits, claim_probability, rate_probability, claim_truth_assessment_inaccuracy)
            self.agents.append(new_agent)
            logger.debug("Created: " + str(new_agent))

    def simulate(self, seed=None):
        if self.reputation_strategy is None:
            raise helpers.ConfigurationError("simulation can't start without a reputation strategy, none found")
        if  self.results_processor is None:
            raise helpers.ConfigurationError("simulation can't start without a results processor, none found")

        self.log_state()
        self.rng.seed(seed)
        if seed: logger.info("RNG seeded with '{}'".format(seed))
        else: logger.info("RNG seeded with a random seed")
        logger.info("Simulation started")
        for sim_round in range(0,config.get("SIM_ROUND_MAX")):
            helpers.current_sim_round = sim_round
            logger.debug("Beginning round #{}".format(sim_round))
            new_claims = self.make_claims()
            self.rate_claims(new_claims)
            self.apply_improvements()
            self.calculate_reputations()
            self.results_processor.process(
                helpers.SimulationEvent.END_OF_ROUND,
                agents_data=self.agents,
                round_number=sim_round)
        logger.info("Simulation finished")

    def make_claims(self):
        all_new_claims = []
        # give all agents one opportunity to claim
        for agent in self.agents:
            new_claim = agent.give_claim_opportunity(self.rng)
            if new_claim is not None:
                all_new_claims.append(new_claim)

        return all_new_claims
            
    def rate_claims(self, claims):
        for claim in claims:
            # give all agents one opportunity to rate
            # only if they are not the claimer
            for agent in self.agents:
                if agent is not claim.author():
                    agent.give_rate_opportunity(claim, self.rng)

    def show(self):
        logger.debug("Round #{} of 0..{}".format(helpers.current_sim_round, config.get("SIM_ROUND_MAX")-1))
        logger.debug("There are " + str(len(self.agents)) + " agents")
        for agent in self.agents:
            logger.debug("Agent #{:>3}: Rep: {}".format(agent.ID, round(agent.global_reputation,2)))
            if agent.claims:
                string = ""
                for claim in agent.claims:
                    logger.debug("            " + str(claim))

    def apply_improvements(self):
        if self.improvement_handler is not None:
            self.improvement_handler.handle(self.agents)

    def calculate_reputations(self):
        self.reputation_strategy.calculate_reputations(self.agents)

    def reset_system(self):
        logger.debug("Resetting system")
        self.agents = []
        self.reputation_strategy = None
        self.improvement_handler = None

    def log_state(self):
        logger.info("There are " + str(len(self.agents)) + " agents")
        logger.info("{:^10} {:^30} {:^30} {:^16} {:^6} {:>6} {:^6}".format(
            "#","DISTORT STRATEGY", "RATING STRATEGY", "claim limits", "claim%", "rate%", "CTAI"))
        for agent in self.agents:
            logger.info(str(agent))