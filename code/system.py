import random

import config as CFG
import agent
from agent import Agent


class System:

    def __init__(self):
        self.agents = [Agent() for i in range(0,CFG.NUM_AGENTS)]

    def simulate(self):
        for _ in range(0,CFG.SIM_ROUND_MAX):
            self.make_claims_and_rate()
            # recalculate reputations
            # apply improvement methods

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
        print("there are " + str(len(self.agents)) + " agents")
        for agent in self.agents:
            agent.print_claims_ratings()

    #def calculate_global_reputations(self,):
