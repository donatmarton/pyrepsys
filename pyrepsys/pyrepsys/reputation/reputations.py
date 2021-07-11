from .reputation_base import ReputationStrategy
import pyrepsys.config
from pyrepsys.errors import UncompleteInitializationError

config = pyrepsys.config.getConfigurator()


class ReputationAverageStrategy(ReputationStrategy):
    def calculate_reputations(self, agents):
        for agent in agents:
            scores = []
            for claim in agent.claims:
                for review in claim.reviews:
                    scores.append(review.value)
            if scores: 
                reputation = sum(scores) / len(scores)
            else: 
                reputation = config.get("INITIAL_REPUTATION")
            agent.global_reputation = reputation

class ReputationWeightedAverage(ReputationStrategy):
    def calculate_reputations(self, agents):
        for agent in agents:
            scores = []
            weights = []
            for claim in agent.claims:
                for review in claim.reviews:
                    scores.append(review.value)
                    review_author = review.author()
                    if review_author is None:
                        raise UncompleteInitializationError("a review is missing its author link")
                    weights.append(review_author.weight)
            if scores: 
                weighted_sum = 0
                for s, w in zip(scores,weights):
                    weighted_sum += s*w
                reputation = weighted_sum/sum(weights)
            else: 
                reputation = config.get("INITIAL_REPUTATION")
            agent.global_reputation = reputation

class BasedOnAvgDifferenceOfClaimsAndReviews(ReputationStrategy):
    def calculate_reputations(self, agents):
        min_rating = config.get("MIN_RATING")
        max_rating = config.get("MAX_RATING")
        min_reputation = min_rating
        max_reputation = max_rating
        max_difference = max_rating - min_rating

        for agent in agents:
            differences = []

            for claim in agent.claims:
                reviews = []
                for review in claim.reviews:
                    reviews.append(review.value)
                if reviews:
                    avg_review_for_claim = sum(reviews) / len(reviews)
                    diff = abs(avg_review_for_claim - claim.author_review.value)
                    # for review and claim value to be "compatible" / directly comparable, 
                    # must note that review score means:
                    # that "this claim should have been an x"
                    # and not "this claim quality is x out of 9"
                    # and also review also not a review of the claimer itself
                    # i.e. both claim (=author review) and review judge the quality behind a claim
                    differences.append(diff)

            if differences:
                avg_diff = sum(differences) / len(differences)
                diff_percent = (max_difference - avg_diff) / max_difference
                reputation = min_reputation + (max_reputation - min_reputation) * diff_percent
            else:
                reputation = config.get("INITIAL_REPUTATION")
            agent.global_reputation = reputation