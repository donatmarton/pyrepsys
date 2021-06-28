from .behavior_base import RateStrategy
import pyrepsys.config

config = pyrepsys.config.getConfigurator()


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
        return claim.author_review.value + inaccuracy

class RateFromOwnExperience(RateStrategy):
    def rate_claim(self, rater, claim, random_seed=None):
        return rater.measure_claim(claim, self.rng(random_seed))

class RateDoNothing(RateStrategy):
    def rate_claim(self, rater, claim, random_seed=None):
        return claim.author_review.value