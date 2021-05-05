import random

import config as CFG
import behavior as beh
from helpers import force_within_bounds

class Agent:
    count = 0
    def __init__(self, rating_strategy, distort_strategy):
        self.ID = Agent.count
        Agent.count += 1
        self.global_reputation = CFG.INITIAL_REPUTATION
        self.claims = []
        self.reviews = []
        self.rating_strategy = rating_strategy
        self.distort_strategy = distort_strategy

    @property
    def distort_strategy(self):
        return self._distort_strategy

    @distort_strategy.setter
    def distort_strategy(self, distort_strategy):
        self._distort_strategy = distort_strategy

    @property
    def rating_strategy(self):
        return self._rating_strategy

    @rating_strategy.setter
    def rating_strategy(self, rating_strategy):
        self._rating_strategy = rating_strategy

    def make_new_claim(self):
        ground_truth = random.uniform(CFG.MIN_RATING, CFG.MAX_RATING)
        measurement_error = random.uniform(-1*CFG.MEASUREMENT_ERROR/2, CFG.MEASUREMENT_ERROR/2)
        measured_claim = force_within_bounds(ground_truth + measurement_error)
        distorted_claim = self.distort_strategy.execute(measured_claim)
        claim = Claim(self.ID, ground_truth, round(distorted_claim))
        self.claims.append(claim)

    def rate_claim(self, claim):
        rating_value = self.rating_strategy.rate_claim(claim)
        review = Review(self.ID, rating_value)
        claim.add_review(review)
        self.reviews.append(review)
   
class Claim:
    count = 0
    def __init__(self, author_ID, ground_truth, claim_value, stake=0):
        self.ID = Claim.count
        Claim.count += 1
        self.author_ID = author_ID
        self.ground_truth = ground_truth # TODO should be private or limited access something
        self.value = claim_value
        self.stake = stake
        self.reviews = []

    def add_review(self,review):
        self.reviews.append(review)

    def __str__(self):
        return "c{}-{}".format(self.value, "".join([str(r) for r in self.reviews]))

class Review:
    def __init__(self, author_ID, rating_value):
        self.author_ID = author_ID
        self.value = rating_value

    def __str__(self):
        return "{}".format(self.value)