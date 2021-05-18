import random

from config import DefaultConfig as CFG
from agent import Agent
import behavior as beh
import helpers

class System:

    def __init__(self, reputation_strategy):
        self.reputation_strategy = reputation_strategy
        self.agents = [Agent(beh.RateHigherHalfRandom(), beh.DistortDoNothingStrategy()) for i in range(0,CFG.NUM_AGENTS)]
        self.improvement_handler = None
        self.rng = random.Random()

    @property
    def reputation_strategy(self):
        return self._reputation_strategy

    @reputation_strategy.setter
    def reputation_strategy(self, reputation_strategy):
        self._reputation_strategy = reputation_strategy

    def simulate(self, seed=None):
        self.rng.seed(seed)
        for sim_round in range(0,CFG.SIM_ROUND_MAX):
            helpers.current_sim_round = sim_round
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
        self.improvement_handler.handle(self.agents)

    def calculate_reputations(self):
        for agent in self.agents:
            agent.global_reputation = self.reputation_strategy.calculate_reputation(agent)