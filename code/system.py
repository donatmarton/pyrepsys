import random
import logging

from config import DefaultConfig as CFG
from agent import Agent
import behavior as beh
import helpers

class System:

    def __init__(self, reputation_strategy=None):
        self._reputation_strategy = reputation_strategy
        self.agents = []
        self._improvement_handler = None
        self.rng = random.Random()

    @property
    def reputation_strategy(self):
        return self._reputation_strategy

    @reputation_strategy.setter
    def reputation_strategy(self, reputation_strategy):
        self._reputation_strategy = reputation_strategy
        logging.info("Reputation strategy set to '{}'".format(type(reputation_strategy)))

    @property
    def improvement_handler(self):
        return self._improvement_handler

    @improvement_handler.setter
    def improvement_handler(self, improvement_handler):
        self._improvement_handler = improvement_handler
        logging.info("Improvement handler entry set to '{}'".format(type(improvement_handler)))

    def create_agents(self, rate_strategy, distort_strategy, amount=1):
        for _ in range(0,amount):
            new_agent = Agent(rate_strategy, distort_strategy)
            self.agents.append(new_agent)
            logging.debug("Created: " + str(new_agent))

    def simulate(self, seed=None):
        assert self.reputation_strategy is not None
        self.log_state()
        self.rng.seed(seed)
        logging.debug("RNG seeded with '{}'".format(seed))
        for sim_round in range(0,CFG.SIM_ROUND_MAX):
            helpers.current_sim_round = sim_round
            logging.debug("Beginning round #{}".format(sim_round))
            new_claims = self.make_claims()
            self.rate_claims(new_claims)
            self.apply_improvements()
            self.calculate_reputations()

    def make_claims(self):
        # select agents that will claim
        num_claimers = self.rng.randint(0,len(self.agents))
        claimers = self.rng.sample(self.agents, num_claimers)
        all_new_claims = []
        for claimer in claimers:
            new_claim = claimer.make_new_claim(self.rng)
            all_new_claims.append(new_claim)
        return all_new_claims
            

    def rate_claims(self, claims):
        for claim in claims:
            self.__rate_claim(claim)

    def __rate_claim(self, claim):
        # select agents that will rate
        num_raters = self.rng.randint(0,CFG.NUM_MAX_RATERS)
        raters = self.rng.sample(self.agents, num_raters)
        for rater in raters:
            rater.rate_claim(claim, self.rng)

    def show(self):
        print("Round #{} of 0..{}".format(helpers.current_sim_round, CFG.SIM_ROUND_MAX-1))
        print("There are " + str(len(self.agents)) + " agents")
        for agent in self.agents:
            print("Agent #{:>2}".format(agent.ID), end = ": ")
            print("Rep: {}".format(round(agent.global_reputation,2)))
            if agent.claims:
                for claim in agent.claims:
                    print("           ", end = "")
                    print(claim)

    def apply_improvements(self):
        if self.improvement_handler is None:
            logging.warning("Improvements NOT performed as none were given.")
        else:
            self.improvement_handler.handle(self.agents)

    def calculate_reputations(self):
        for agent in self.agents:
            agent.global_reputation = self.reputation_strategy.calculate_reputation(agent)

    def log_state(self):
        logging.info("Reputation strategy: '{}'".format(type(self.reputation_strategy).__name__))
        logging.info("Improvement handler chain entry point: '{}'".format(type(self.improvement_handler).__name__))
        logging.info("There are " + str(len(self.agents)) + " agents")
        logging.info("{:^9} {:^30} {:^30}".format("#","DISTORT STRATEGY", "RATING STRATEGY"))
        for agent in self.agents:
            logging.info(str(agent))