import copy

#

from .reputation_base import AbstractHandler
import pyrepsys.config as config
import pyrepsys.helpers as helpers


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