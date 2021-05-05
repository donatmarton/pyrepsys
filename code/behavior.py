from abc import ABC, abstractmethod
import random
import math

import config as CFG
from helpers import force_within_bounds

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

class DistortRoundUpStrategy(DistortStrategy):
    def execute(self, truth):
        return force_within_bounds( math.ceil(truth) )

class DistortUpWithinMeasurementError(DistortStrategy):
    def execute(self, truth):
        return force_within_bounds( round(truth + random.uniform(0, CFG.MEASUREMENT_ERROR/2)) )