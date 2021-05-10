import random

from config import DefaultConfig as CFG
import agent
from agent import Agent
import behavior as beh
import helpers

class System:

    def __init__(self, reputation_strategy):
        self.reputation_strategy = reputation_strategy
        self.agents = [Agent(beh.RateHigherHalfRandom(), beh.DistortDoNothingStrategy()) for i in range(0,CFG.NUM_AGENTS)]
        self.improvement_handler = None

    @property
    def reputation_strategy(self):
        return self._reputation_strategy

    @reputation_strategy.setter
    def reputation_strategy(self, reputation_strategy):
        self._reputation_strategy = reputation_strategy

    def simulate(self):
        for sim_round in range(0,CFG.SIM_ROUND_MAX):
            helpers.current_sim_round = sim_round
            self.make_claims_and_rate()
            self.apply_improvements_and_reputation()

            # what is ideal division of tasks to functions

    def make_claims_and_rate(self):
        # select agents that will claim
        num_claimers = random.randint(0,len(self.agents))
        claimers = random.sample(self.agents, num_claimers)
        for claimer in claimers:
            claimer.make_new_claim()
            self.__rate_claim(claimer.claims[-1]) # -1 gets last claim from agent
            # TODO: restricted access to claims ?

    def __rate_claim(self, claim):
        # select agents that will rate
        num_raters = random.randint(0,CFG.NUM_MAX_RATERS)
        raters = random.sample(self.agents, num_raters)
        for rater in raters:
            rater.rate_claim(claim)

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

    def apply_improvements_and_reputation(self):
        self.improvement_handler.handle(self.agents)
        for agent in self.agents:
            agent.global_reputation = self.reputation_strategy.calculate_reputation(agent)