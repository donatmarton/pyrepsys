from abc import ABC, abstractmethod

from pyrepsys.helper_types import LocalConfig


class ReputationStrategy(ABC, LocalConfig):
    @abstractmethod
    def calculate_reputations(self, agents):
        pass

class AbstractHandler(ABC, LocalConfig):
    def __init__(self):
        super().__init__()
        self._next_handler = None
    
    def set_next(self, handler):
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, request):
        if self._next_handler:
            return self._next_handler.handle(request)
        return None