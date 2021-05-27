import weakref

import config
import helpers


class Agent:
    count = 0
    def __init__(self, rating_strategy, distort_strategy):
        self.ID = Agent.count
        Agent.count += 1
        self.global_reputation = config.get("INITIAL_REPUTATION")
        self.claims = []
        self.reviews = []
        self.rating_strategy = rating_strategy
        self.distort_strategy = distort_strategy
        self.weight = 1

    def __del__(self):
        Agent.count -= 1

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

    def make_new_claim(self, rng):
        ground_truth = rng.random()
        cfg_MEASUREMENT_ERROR = config.get("MEASUREMENT_ERROR")
        measurement_error = rng.uniform(-1*cfg_MEASUREMENT_ERROR/2, cfg_MEASUREMENT_ERROR/2)
        measured_claim = helpers.force_internal_bounds(ground_truth + measurement_error)
        distorted_claim_ae = self.distort_strategy.execute(
            helpers.i2a(measured_claim),
            rng.random())
        distorted_claim_ae = helpers.force_agent_exposed_bounds(distorted_claim_ae)
        claim = Claim(weakref.ref(self), ground_truth, helpers.a2i(distorted_claim_ae))
        self.claims.append(claim)
        return claim

    def rate_claim(self, claim, rng):
        review_score_ae = self.rating_strategy.execute(claim, rng.random())
        review_score_ae = helpers.force_agent_exposed_bounds(review_score_ae)
        review = Review(weakref.ref(self), helpers.a2i(review_score_ae))
        claim.add_review(review)
        self.reviews.append(review)

    def __str__(self):
        return "Agent {:>2}: {:<30} {:<30}".format(
                self.ID,
                type(self._distort_strategy).__name__,
                type(self._rating_strategy).__name__
        )
   
class Claim:
    count = 0
    def __init__(self, author, ground_truth_i, claim_score_i, stake=0):
        self.ID = Claim.count
        Claim.count += 1
        self.author = author
        self._ground_truth_i = ground_truth_i
        self._score_i = claim_score_i
        self.stake = stake
        self.reviews = []
        self.round_timestamp = helpers.current_sim_round

    def __del__(self):
        Claim.count -= 1

    def add_review(self,review):
        self.reviews.append(review)

    @property
    def value(self):
        return helpers.i2a(self._score_i)

    @property
    def ground_truth(self):
        return helpers.i2a(self._ground_truth_i)

    def __str__(self):
        return "c{}a{}-{}".format(self.value, self.round_timestamp, 
            " ".join([str(r)+"w"+str(round(r.author().weight,2)) for r in self.reviews]))
            

class Review:
    def __init__(self, author, rating_score_i):
        self.author = author
        self._score_i = rating_score_i

    @property
    def value(self):
        return helpers.i2a(self._score_i)

    @value.setter
    def value(self, score_ae):
        self._score_i = helpers.a2i(score_ae)

    def __str__(self):
        return "{}".format(self.value)