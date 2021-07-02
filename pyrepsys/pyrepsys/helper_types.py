from enum import Enum, auto
from collections import namedtuple

from pyrepsys.errors import ConfigurationError


class SimulationEvent(Enum):
    BEGIN_SCENARIO = auto()
    END_OF_ROUND = auto()
    END_OF_SCENARIO = auto()
    END_OF_SIMULATION = auto()

ClaimLimits = namedtuple("ClaimLimits",["min","max"])

class ResolutionDomain(Enum):
    MEASURED_CLAIM = auto()
    REVIEW = auto()

class LocalConfig():
    def __init__(self):
        self.local_config = None

    def get_local_config(self, config_name):
        try:
            cfg_value = self.local_config[config_name]
        except KeyError:
            raise ConfigurationError("'{}' requested, it's not in local config".format(config_name))
        except TypeError:
            raise ConfigurationError("'{}' requested, no local config found".format(config_name))
        return cfg_value