import random
import logging

import config
from agent import Agent
import helpers


class System:

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
        logging.info("Reputation strategy set to '{}'".format(type(reputation_strategy).__name__))

    @property
    def improvement_handler(self):
        return self._improvement_handler

    @improvement_handler.setter
    def improvement_handler(self, improvement_handler):
        self._improvement_handler = improvement_handler
        logging.info("Improvement handler entry set to '{}'".format(type(improvement_handler).__name__))

    def create_agents(self, distort_strategy, rate_strategy, claim_limits, claim_probability, rate_probability, claim_truth_assessment_inaccuracy, amount=1):
        for _ in range(0,amount):
            new_agent = Agent(distort_strategy, rate_strategy, claim_limits, claim_probability, rate_probability, claim_truth_assessment_inaccuracy)
            self.agents.append(new_agent)
            logging.debug("Created: " + str(new_agent))

    def simulate(self, seed=None):
        assert self.reputation_strategy is not None
        assert self.results_processor is not None
        self.log_state()
        self.rng.seed(seed)
        logging.debug("RNG seeded with '{}'".format(seed))
        for sim_round in range(0,config.get("SIM_ROUND_MAX")):
            helpers.current_sim_round = sim_round
            logging.debug("Beginning round #{}".format(sim_round))
            new_claims = self.make_claims()
            self.rate_claims(new_claims)
            self.apply_improvements()
            self.calculate_reputations()
            self.results_processor.process(
                helpers.SimulationEvent.END_OF_ROUND,
                agents_data=self.agents,
                round_number=sim_round)

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
            self.__rate_claim(claim)

    def __rate_claim(self, claim):
        # give all agents one opportunity to rate
        for agent in self.agents:
            agent.give_rate_opportunity(claim, self.rng)

    def show(self):
        logging.info("Round #{} of 0..{}".format(helpers.current_sim_round, config.get("SIM_ROUND_MAX")-1))
        logging.info("There are " + str(len(self.agents)) + " agents")
        for agent in self.agents:
            logging.info("Agent #{:>3}: Rep: {}".format(agent.ID, round(agent.global_reputation,2)))
            if agent.claims:
                string = ""
                for claim in agent.claims:
                    logging.info("            " + str(claim))

    def apply_improvements(self):
        if self.improvement_handler is None:
            logging.warning("Improvements NOT performed as none were given.")
        else:
            self.improvement_handler.handle(self.agents)

    def calculate_reputations(self):
        for agent in self.agents:
            agent.global_reputation = self.reputation_strategy.calculate_reputation(agent)

    def reset_system(self):
        logging.debug("Resetting system")
        self.agents = []
        self.reputation_strategy = None
        self.improvement_handler = None

    def log_state(self):
        logging.info("Reputation strategy: '{}'".format(type(self.reputation_strategy).__name__))
        logging.info("Improvement handler chain entry point: '{}'".format(type(self.improvement_handler).__name__))
        logging.info("There are " + str(len(self.agents)) + " agents")
        logging.info("{:^10} {:^30} {:^30} {:^16} {:^6} {:>6} {:^6}".format(
            "#","DISTORT STRATEGY", "RATING STRATEGY", "claim limits", "claim%", "rate%", "CTAI"))
        for agent in self.agents:
            logging.info(str(agent))