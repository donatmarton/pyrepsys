#

#

from .behavior_base import DistortStrategy
import pyrepsys.config as config
from pyrepsys.helpers import force_agent_exposed_bounds


class DistortDoNothingStrategy(DistortStrategy):
    def distort(self, distorter, measured_truth, random_seed=None):
        return measured_truth

class DistortUpByOneAlways(DistortStrategy):
    def distort(self, distorter, measured_truth, random_seed=None):
        return force_agent_exposed_bounds( measured_truth + 1 )

class DistortUpByOneRandom(DistortStrategy):
    def distort(self, distorter, measured_truth, random_seed=None):
        return force_agent_exposed_bounds( measured_truth + self.rng(random_seed).randint(0,1) )

class DistortHugeUpRandom(DistortStrategy):
    def distort(self, distorter, measured_truth, random_seed=None):
        leeway = config.get("MAX_RATING") - measured_truth
        distorted_truth = measured_truth + self.rng(random_seed).uniform(
            leeway/2,
            leeway)
        distorted_truth = round(distorted_truth, config.get("DECIMAL_PRECISION"))
        return force_agent_exposed_bounds( distorted_truth )