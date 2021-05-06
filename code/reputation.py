from abc import ABC, abstractmethod
import copy

import config as CFG
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
            reputation = CFG.INITIAL_REPUTATION
        return reputation
        #return helpers.force_within_bounds( agent.weight * reputation )




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
        for agent in agents:
            for claim in copy.copy( agent.claims ):
                if helpers.current_sim_round - claim.round_timestamp > CFG.AGING_LIMIT:
                    agent.claims.remove(claim)
                    # also remove from an agent's own reviews list
        return super().handle(agents)


class WeightedReputation(AbstractHandler):
    """
    the better an agent's reputation, the more weight his reviews have
    """
    def handle(self, agents):
        for agent in agents:
            agent.weight *= (agent.global_reputation - CFG.MIN_RATING) / (CFG.MAX_RATING - CFG.MIN_RATING)
        return super().handle(agents)


class StakeBasedReputation(AbstractHandler):
    def handle(self, agents):
        return super().handle(agents)




