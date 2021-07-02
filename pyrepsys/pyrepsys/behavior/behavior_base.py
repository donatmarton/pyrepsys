from abc import ABC, abstractmethod
import random

from pyrepsys.agent import Claim
from pyrepsys.helper_types import LocalConfig


class BehaviorStrategy(ABC, LocalConfig):
    @abstractmethod
    def execute(self, executor_agent, data, random_seed=None):
        pass

    def rng(self, seed=None):
        if seed:
            return random.Random(seed)
        else:
            return random

class RateStrategy(BehaviorStrategy):
    def execute(self, executor_agent, data, random_seed=None):
        if isinstance(data, Claim):
            return self.rate_claim(executor_agent, data, random_seed)
        else:
            raise TypeError

    @abstractmethod
    def rate_claim(self, rater, claim, random_seed=None):
        pass

class DistortStrategy(BehaviorStrategy):
    def execute(self, executor_agent, data, random_seed=None):
        if isinstance(data, int) or isinstance(data, float):
            return self.distort(executor_agent, data, random_seed)
        else:
            raise TypeError

    @abstractmethod
    def distort(self, distorter, measured_truth, random_seed=None):
        pass