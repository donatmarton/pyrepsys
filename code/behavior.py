from abc import ABC, abstractmethod

import config as CFG


class RateStrategy(ABC):
    @abstractmethod
    def rate_claim(self, claim):
        pass

class RateExampleStrategy1(RateStrategy):
    def rate_claim(self, claim):
        return min(claim.value + 1, CFG.MAX_RATING)

class DistortStrategy(ABC):
    @abstractmethod
    def distort_ground_truth(self, ground_truth):
        pass

class DistortExampleStrategy1(DistortStrategy):
    def distort_ground_truth(self, ground_truth):
        return min(ground_truth + 1, CFG.MAX_RATING)

"""
def rating_function_1(claim):
    return min(claim.value + 1, CFG.MAX_RATING)

def distortion_fun_1(claim_value):
    return min(claim_value + 1, CFG.MAX_RATING)
"""