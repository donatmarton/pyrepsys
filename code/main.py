import random

import system
import reputation as rep
import behavior as beh

# TODO how to organize multiple rounds of claim,rate etc.. simulation ?
# TODO how to incorporate global reputation into decision making, if at all ?
# TODO how to link to type of variable, e.g. in system make claims to agent class, so I can ctrl-jump to definition
# TODO find a way to specify&control agent behavior from here, I dont want to "import behavior as beh" in system.py

def simulate():
    sys = system.System(rep.ReputationAverageStrategy())

    aging = rep.Aging()
    weights = rep.WeightedReputation()
    stakes = rep.StakeBasedReputation()
    aging.set_next(weights).set_next(stakes)

    sys.improvement_handler = aging

    seed = random.random()
    sys.simulate(seed)
    sys.show()


if __name__ == "__main__":
    simulate()