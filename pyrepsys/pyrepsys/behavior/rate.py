from .behavior_base import RateStrategy
import pyrepsys.config
from pyrepsys.errors import ConfigurationError

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

class RateLinearManipulation(RateStrategy):
    def rate_claim(self, rater, claim, random_seed=None):
        a = self.get_local_config("a")
        b = self.get_local_config("b")
        return b + a * claim.author_review.value

class RateInvertedSlope(RateStrategy):
    def rate_claim(self, rater, claim, random_seed=None):
        max_rating = config.get("MAX_RATING")
        min_rating = config.get("MIN_RATING")
        return -1 * claim.author_review.value + max_rating + min_rating

class Flatten(RateStrategy):
    def rate_claim(self, rater, claim, random_seed=None):
        max_rating = config.get("MAX_RATING")
        min_rating = config.get("MIN_RATING")
        mid = (max_rating - min_rating) * 0.5 + min_rating
        a = self.get_local_config("a")
        return a * (claim.author_review.value - mid) + mid

class LinearBreakpointed(RateStrategy):
    def rate_claim(self, rater, claim, random_seed=None):
        dir = self.get_local_config("dir")
        a = self.get_local_config("a")
        b = self.get_local_config("b")
        brpoint = self.get_local_config("brpoint")
        brpointval = self.get_local_config("brpointval")
        c_val = claim.author_review.value
        if dir == "incr":
            return brpointval if c_val >= brpoint else b + a * c_val
        elif dir == "decr":
            return brpointval if c_val <= brpoint else b + a * c_val
        else:
            raise ConfigurationError

class SecondOrderPolynomial(RateStrategy):
    def rate_claim(self, rater, claim, random_seed=None):
        a = self.get_local_config("a")
        b = self.get_local_config("b")
        c = self.get_local_config("c")
        dir = self.get_local_config("dir")
        c_val = claim.author_review.value
        if dir == "incr":
            return c_val + (c + b * c_val + a * c_val * c_val)
        elif dir == "decr":
            return c_val - (c + b * c_val + a * c_val * c_val)
        else:
            raise ConfigurationError

class RandomBigError(RateStrategy):
    def rate_claim(self, rater, claim, random_seed=None):
        chance = self.get_local_config("chance")
        if self.rng(random_seed).random() >= chance:
            return config.get("MAX_RATING")
        else:
            return rater.measure_claim(claim)
