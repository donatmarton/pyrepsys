import random

from config import DefaultConfig as CFG
import behavior as beh
import helpers


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
        self.weight = 1 #TODO unused, for weighted reputation calculation

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
        ground_truth = random.random()
        measurement_error = random.uniform(-1*CFG.MEASUREMENT_ERROR/2, CFG.MEASUREMENT_ERROR/2)
        measured_claim = helpers.force_internal_bounds(ground_truth + measurement_error)
        distorted_claim = helpers.a2i(self.distort_strategy.execute(helpers.i2a(measured_claim)))
        claim = Claim(self.ID, ground_truth, distorted_claim)
        self.claims.append(claim)
        return claim

    def rate_claim(self, claim):
        review_score_ae = self.rating_strategy.rate_claim(claim)
        review = Review(self.ID, helpers.a2i(review_score_ae))
        claim.add_review(review)
        self.reviews.append(review)
   
class Claim:
    count = 0
    def __init__(self, author_ID, ground_truth_i, claim_score_i, stake=0):
        self.ID = Claim.count
        Claim.count += 1
        self.author_ID = author_ID
        self.ground_truth = ground_truth_i # TODO should be private or limited access something
        self._score_i = claim_score_i
        self.stake = stake
        self.reviews = []
        self.round_timestamp = helpers.current_sim_round

    def add_review(self,review):
        self.reviews.append(review)

    @property
    def value(self):
        return helpers.i2a(self._score_i)

    @value.setter
    def value(self, score_ae):
        self._score_i = helpers.a2i(score_ae)

    def __str__(self):
        return "c{}a{}-{}".format(self.value, self.round_timestamp, " ".join([str(r) for r in self.reviews]))

class Review:
    def __init__(self, author_ID, rating_score_i):
        self.author_ID = author_ID
        self._score_i = rating_score_i

    @property
    def value(self):
        return helpers.i2a(self._score_i)

    @value.setter
    def value(self, score_ae):
        self._score_i = helpers.a2i(score_ae)

    def __str__(self):
        return "{}".format(self.value)