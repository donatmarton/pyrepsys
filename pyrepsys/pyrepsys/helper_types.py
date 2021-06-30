from enum import Enum, auto
from collections import namedtuple


class SimulationEvent(Enum):
    BEGIN_SCENARIO = auto()
    END_OF_ROUND = auto()
    END_OF_SCENARIO = auto()
    END_OF_SIMULATION = auto()

ClaimLimits = namedtuple("ClaimLimits",["min","max"])

class ResolutionDomain(Enum):
    MEASURED_CLAIM = auto()
    REVIEW = auto()