from abc import ABC, abstractmethod
import copy

import config
import helpers

class ReputationStrategy(ABC):
    @abstractmethod
    def calculate_reputation(self, agent):
        pass

class ReputationAverageStrategy(ReputationStrategy):
    def calculate_reputation(self, agent):
        scores = []
        for claim in agent.claims:
            for review in claim.reviews:
                scores.append(review.value)
        if scores: 
            reputation = sum(scores) / len(scores)
        else: 
            reputation = config.get("INITIAL_REPUTATION")
        return reputation

class ReputationWeightedAverage(ReputationStrategy):
    def calculate_reputation(self, agent):
        scores = []
        weights = []
        for claim in agent.claims:
            for review in claim.reviews:
                scores.append(review.value)
                review_author = review.author()
                assert review_author is not None
                weights.append(review_author.weight)
        if scores: 
            weighted_sum = 0
            for s, w in zip(scores,weights):
                weighted_sum += s*w
            reputation = weighted_sum/sum(weights)
        else: 
            reputation = config.get("INITIAL_REPUTATION")
        return reputation




class Handler(ABC):
    @abstractmethod
    def set_next(self, handler):
        pass

    @abstractmethod
    def handle(self, request):
        pass


class AbstractHandler(Handler):
    _next_handler = None
    
    def set_next(self, handler):
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, request):
        if self._next_handler:
            return self._next_handler.handle(request)
        return None


class Aging(AbstractHandler):
    def handle(self, agents):
        aging_limit = config.get("AGING_LIMIT")
        for agent in agents:
            for claim in copy.copy( agent.claims ):
                if helpers.current_sim_round - claim.round_timestamp > aging_limit:
                    agent.claims.remove(claim)
                    
        return super().handle(agents)


class Weights(AbstractHandler):
    """
    the better an agent's reputation, the more weight his reviews have
    """
    def handle(self, agents):
        min_rating = config.get("MIN_RATING")
        max_rating = config.get("MAX_RATING")
        for agent in agents:
            agent.weight = (agent.global_reputation - min_rating) / (max_rating - min_rating)
        return super().handle(agents)


class StakeBasedReputation(AbstractHandler):
    def handle(self, agents):
        return super().handle(agents)




