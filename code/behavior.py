from abc import ABC, abstractmethod
import random
import math

from config import DefaultConfig as CFG
from helpers import force_agent_exposed_bounds

class RateStrategy(ABC):
    @abstractmethod
    def rate_claim(self, claim):
        pass

class RateRandomStrategy(RateStrategy):
    def rate_claim(self, claim):
        return random.randint(CFG.MIN_RATING, CFG.MAX_RATING)

class RateLowerHalfRandom(RateStrategy):
    def rate_claim(self, claim):
        return random.randint(CFG.MIN_RATING, CFG.MAX_RATING//2)

class RateHigherHalfRandom(RateStrategy):
    def rate_claim(self, claim):
        return random.randint(CFG.MAX_RATING//2, CFG.MAX_RATING)




class DistortStrategy(ABC):
    @abstractmethod
    def execute(self, truth):
        pass

class DistortDoNothingStrategy(DistortStrategy):
    def execute(self, truth):
        return truth

class DistortUpByOneAlways(DistortStrategy):
    def execute(self, truth):
        return force_agent_exposed_bounds( truth + 1 )

class DistortUpByOneRandom(DistortStrategy):
    def execute(self, truth):
        return force_agent_exposed_bounds( truth + random.randint(0,1) )