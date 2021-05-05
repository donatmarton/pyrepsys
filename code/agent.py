import random

import config as CFG
import behavior as beh

class Agent:
    count = 0
    def __init__(self, rating_strategy, distort_strategy):
        self.ID = Agent.count
        Agent.count += 1
        self.global_reputation = CFG.INITIAL_REPUTATION
        self.claims = []
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
        ground_truth = random.randint(CFG.MIN_RATING, CFG.MAX_RATING)
        distorted_claim = self.distort_strategy.distort_ground_truth(ground_truth)
        claim = Claim(self.ID, ground_truth, distorted_claim)
        self.claims.append(claim)

    def rate_claim(self, claim):
        rating_value = self.rating_strategy.rate_claim(claim)
        rating = Rating(self.ID, rating_value)
        claim.add_rating(rating)
   
class Claim:
    count = 0
    def __init__(self, author_ID, ground_truth, claim_value, stake=0):
        self.ID = Claim.count
        Claim.count += 1
        self.author_ID = author_ID
        self.ground_truth = ground_truth # TODO should be private or limited access something
        self.value = claim_value
        self.stake = stake
        self.ratings = []

    def add_rating(self,rating):
        self.ratings.append(rating)

    def __str__(self):
        return "c{}-{}".format(self.value, "".join([str(x) for x in self.ratings]))

class Rating:
    def __init__(self, author_ID, rating_value):
        self.author_ID = author_ID
        self.value = rating_value

    def __str__(self):
        return "{}".format(self.value)