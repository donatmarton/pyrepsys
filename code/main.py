import random
import os
from datetime import datetime

import system
import reputation as rep
import behavior as beh

# TODO how to organize multiple rounds of claim,rate etc.. simulation ?
# TODO how to incorporate global reputation into decision making, if at all ?
# TODO how to link to type of variable, e.g. in system make claims to agent class, so I can ctrl-jump to definition
# TODO find a way to specify&control agent behavior from here, I dont want to "import behavior as beh" in system.py

def simulate():

    reputation_strategy = rep.ReputationWeightedAverage()
    #reputation_strategy = rep.ReputationAverageStrategy()

    sys = system.System( reputation_strategy )

    aging = rep.Aging()
    weights = rep.Weights()
    stakes = rep.StakeBasedReputation()
    aging.set_next(weights).set_next(stakes)

    sys.improvement_handler = aging

    seed = random.random()
    sys.simulate(seed)
    sys.show()

def prepare_for_artifacts():
        code_files_path = os.path.dirname( os.path.abspath(__file__) )
        project_root_path = os.path.join( code_files_path, os.pardir )
        simulation_artifacts_path = os.path.join( project_root_path, "simulation_artifacts" )

        now = datetime.now()
        # create sim dir name: run_YYYY-MM-DD_HH:MM:SS
        simulation_dir_name = now.strftime( "run_%Y-%m-%d_%H:%M:%S" )
        simulation_dir_path = os.path.join( simulation_artifacts_path, simulation_dir_name )
        
        os.makedirs(simulation_dir_path, exist_ok=True)

        symlink = os.path.join( simulation_artifacts_path, "run_latest" )
        try:
            os.remove(symlink)
        except FileNotFoundError:
            pass
        os.symlink(simulation_dir_path, symlink, target_is_directory=True)




if __name__ == "__main__":
    prepare_for_artifacts()
    simulate()