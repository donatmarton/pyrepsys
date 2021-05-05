from abc import ABC, abstractmethod

import config as CFG

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