import system
import reputation as rep
import behavior as beh

# TODO how to organize multiple rounds of claim,rate etc.. simulation ?
# TODO how to incorporate global reputation into decision making, if at all ?
# TODO how to link to type of variable, e.g. in system make claims to agent class, so I can ctrl-jump to definition
# TODO find a way to specify&control agent behavior from here, I dont want to "import behavior as beh" in system.py

sys = system.System(rep.ReputationAverageStrategy())
sys.simulate()
sys.show()

