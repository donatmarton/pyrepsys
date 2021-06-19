import logging
import weakref
import random

import pyrepsys.config
import pyrepsys.helpers as helpers
from pyrepsys.errors import UncompleteInitializationError, PermissionViolatedError

logger = logging.getLogger(__name__)
config = pyrepsys.config.getConfigurator()

class Agent:
    count = 0
    def __init__(self, distort_strategy, rating_strategy, claim_limits, claim_probability, rate_probability, claim_truth_assessment_inaccuracy):
        self.ID = Agent.count
        Agent.count += 1
        self.global_reputation = config.get("INITIAL_REPUTATION")
        self.claims = []
        self.reviews = []
        self.distort_strategy = distort_strategy
        self.rating_strategy = rating_strategy
        self.claim_limits = claim_limits
        self.claim_probability = claim_probability
        self.rate_probability = rate_probability
        self.claim_truth_assessment_inaccuracy = claim_truth_assessment_inaccuracy
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

    def give_claim_opportunity(self, rng):
        rand = rng.random()
        random_seed = rng.random()
        if rand <= self.claim_probability:
            throwaway_rng = random.Random(random_seed)
            new_claim = self.__make_new_claim(throwaway_rng)
        else: new_claim = None
        return new_claim

    def __make_new_claim(self, rng):
        claim = Claim(weakref.ref(self), rng)
        measured_claim_score_ae = self.measure_claim(claim, rng)

        distorted_claim_ae = self.distort_strategy.execute(
            self,
            measured_claim_score_ae,
            rng.random())
        distorted_claim_ae = helpers.convert_resolution(distorted_claim_ae, helpers.ResolutionDomain.REVIEW)
        distorted_claim_ae = helpers.force_agent_exposed_bounds(distorted_claim_ae)
        distorted_claim_i = helpers.a2i(distorted_claim_ae)

        if distorted_claim_i > self.claim_limits.max or distorted_claim_i < self.claim_limits.min:
            # claim would be outside of limits, agent refuses to publish claim
            return None
        else:
            author_review = Review(weakref.ref(self), distorted_claim_i)
            claim.add_author_review(self, author_review)
            self.claims.append(claim)
            return claim

    def give_rate_opportunity(self, claim, rng):
        rand = rng.random()
        random_seed = rng.random()
        if rand <= self.rate_probability:
            throwaway_rng = random.Random(random_seed)
            self.__rate_claim(claim, throwaway_rng)
    
    def __rate_claim(self, claim, rng):
        review_score_ae = self.rating_strategy.execute(self, claim, rng.random())
        review_score_ae = helpers.convert_resolution(review_score_ae, helpers.ResolutionDomain.REVIEW)
        review_score_ae = helpers.force_agent_exposed_bounds(review_score_ae)
        review = Review(weakref.ref(self), helpers.a2i(review_score_ae))
        claim.add_review(review)
        self.reviews.append(review)

    def measure_claim(self, claim, rng):
        max_error_i = self.claim_truth_assessment_inaccuracy
        measurement_error_i = rng.uniform(-1*max_error_i, max_error_i)
        measured_score_i = helpers.force_internal_bounds(claim.ground_truth_i + measurement_error_i)
        measured_score_ae = helpers.i2a(measured_score_i)
        return helpers.convert_resolution(measured_score_ae, helpers.ResolutionDomain.MEASURED_CLAIM)
    
    def __str__(self):
        return "Agent {:>3}: {:<30} {:<30} {:.4f} .. {:.4f} {:>6.0%} {:>6.0%} {:>6.4f}".format(
                self.ID,
                type(self._distort_strategy).__name__,
                type(self._rating_strategy).__name__,
                self.claim_limits.min,
                self.claim_limits.max,
                self.claim_probability,
                self.rate_probability,
                self.claim_truth_assessment_inaccuracy
        )

class Claim:
    count = 0
    def __init__(self, author, rng, author_review=None, stake=None):
        self.ID = Claim.count
        Claim.count += 1
        self.author = author
        self._ground_truth_i = rng.random()
        self._author_review = author_review
        self.stake = stake
        self.reviews = []
        self.round_timestamp = helpers.current_sim_round

    def __del__(self):
        Claim.count -= 1

    def add_review(self, review):
        self.reviews.append(review)

    @property
    def author_review(self):
        if self._author_review is None:
            logger.error("Claim {}: author review accessed but is not yet initialized!".format(self.ID))
            raise UncompleteInitializationError
        else:
            return self._author_review

    def add_author_review(self, adding_agent, review):
        if self._author_review is not None:
            logger.error("Claim {}: Agent {} tried to change existing author review".format(
                self.ID, adding_agent.ID))
            raise PermissionViolatedError
        if adding_agent is not self.author():
            logger.error("Claim {}: Agent {} tried add author review who is not the author! (author: {})".format(
                self.ID, adding_agent.ID, self.author().ID ))
            raise PermissionViolatedError
        if review.author() is not self.author():
            logger.error("Claim {}: Agent {} tried add author review who is not the author! (author: {})".format(
                self.ID, adding_agent.ID, self.author().ID ))
            raise PermissionViolatedError
        
        self._author_review = review

    @property
    def ground_truth(self):
        #logger.warning("Claim {}: agent-exposed ground truth was accessed.".format(self.ID))
        return helpers.i2a(self._ground_truth_i)

    @property
    def ground_truth_i(self):
        return self._ground_truth_i

    def __str__(self):
        return "c{}a{}-{}".format(self.author_review.value, self.round_timestamp, 
            " ".join([str(r)+"w"+str(round(r.author().weight,2)) for r in self.reviews]))
            

class Review:
    def __init__(self, author, rating_score_i):
        self.author = author
        self._score_i = rating_score_i

    @property
    def value(self):
        return helpers.i2a(self._score_i)

    def __str__(self):
        return "{}".format(self.value)