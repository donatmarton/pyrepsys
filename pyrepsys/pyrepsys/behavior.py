from abc import ABC, abstractmethod
import random

import pyrepsys.config as config
from pyrepsys.helpers import force_agent_exposed_bounds
from pyrepsys.agent import Claim




# ABSTRACT CLASSES:

class BehaviorStrategy(ABC):
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




# CONCRETE RATE STRATEGIES:

class RateRandomStrategy(RateStrategy):
    def rate_claim(self, rater, claim, random_seed=None):
        min_rating = config.get("MIN_RATING")
        max_rating = config.get("MAX_RATING")
        return self.rng(random_seed).randint(min_rating, max_rating)

class RateLowerHalfRandom(RateStrategy):
    def rate_claim(self, rater, claim, random_seed=None):
        min_rating = config.get("MIN_RATING")
        max_rating = config.get("MAX_RATING")
        return self.rng(random_seed).randint(min_rating, max_rating//2)

class RateHigherHalfRandom(RateStrategy):
    def rate_claim(self, rater, claim, random_seed=None):
        max_rating = config.get("MAX_RATING")
        return self.rng(random_seed).randint(max_rating//2, max_rating)

class RateNearClaimScore(RateStrategy):
    def rate_claim(self, rater, claim, random_seed=None):
        inaccuracy = self.rng(random_seed).randint(-1, 1)
        return claim.value + inaccuracy

class RateFromOwnExperience(RateStrategy):
    def rate_claim(self, rater, claim, random_seed=None):
        return rater.measure_claim(claim, self.rng(random_seed))

class RateDoNothing(RateStrategy):
    def rate_claim(self, rater, claim, random_seed=None):
        return claim.value




# CONCRETE DISTORT STRATEGIES:

class DistortDoNothingStrategy(DistortStrategy):
    def distort(self, distorter, measured_truth, random_seed=None):
        return measured_truth

class DistortUpByOneAlways(DistortStrategy):
    def distort(self, distorter, measured_truth, random_seed=None):
        return force_agent_exposed_bounds( measured_truth + 1 )

class DistortUpByOneRandom(DistortStrategy):
    def distort(self, distorter, measured_truth, random_seed=None):
        return force_agent_exposed_bounds( measured_truth + self.rng(random_seed).randint(0,1) )

class DistortHugeUpRandom(DistortStrategy):
    def distort(self, distorter, measured_truth, random_seed=None):
        leeway = config.get("MAX_RATING") - measured_truth
        distorted_truth = measured_truth + self.rng(random_seed).uniform(
            leeway/2,
            leeway)
        distorted_truth = round(distorted_truth, config.get("DECIMAL_PRECISION"))
        return force_agent_exposed_bounds( distorted_truth )