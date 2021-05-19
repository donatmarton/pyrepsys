from abc import ABC, abstractmethod
import random

import config
from helpers import force_agent_exposed_bounds
from agent import Claim




# ABSTRACT CLASSES:

class BehaviorStrategy(ABC):
    @abstractmethod
    def execute(self, data, random_seed=None):
        pass

    def rng(self, seed=None):
        if seed:
            return random.Random(seed)
        else:
            return random

class RateStrategy(BehaviorStrategy):
    def execute(self, data, random_seed=None):
        if isinstance(data, Claim):
            return self.rate_claim(data, random_seed)
        else:
            raise TypeError

    @abstractmethod
    def rate_claim(self, claim, random_seed=None):
        pass

class DistortStrategy(BehaviorStrategy):
    def execute(self, data, random_seed=None):
        if isinstance(data, int) or isinstance(data, float):
            return self.distort(data, random_seed)
        else:
            raise TypeError

    @abstractmethod
    def distort(self, truth, random_seed=None):
        pass




# CONCRETE RATE STRATEGIES:

class RateRandomStrategy(RateStrategy):
    def rate_claim(self, claim, random_seed=None):
        return self.rng(random_seed).randint(config.DefaultConfig.MIN_RATING, config.DefaultConfig.MAX_RATING)

class RateLowerHalfRandom(RateStrategy):
    def rate_claim(self, claim, random_seed=None):
        return self.rng(random_seed).randint(config.DefaultConfig.MIN_RATING, config.DefaultConfig.MAX_RATING//2)

class RateHigherHalfRandom(RateStrategy):
    def rate_claim(self, claim, random_seed=None):
        return self.rng(random_seed).randint(config.DefaultConfig.MAX_RATING//2, config.DefaultConfig.MAX_RATING)




# CONCRETE DISTORT STRATEGIES:

class DistortDoNothingStrategy(DistortStrategy):
    def distort(self, truth, random_seed=None):
        return truth

class DistortUpByOneAlways(DistortStrategy):
    def distort(self, truth, random_seed=None):
        return force_agent_exposed_bounds( truth + 1 )

class DistortUpByOneRandom(DistortStrategy):
    def distort(self, truth, random_seed=None):
        return force_agent_exposed_bounds( truth + self.rng(random_seed).randint(0,1) )