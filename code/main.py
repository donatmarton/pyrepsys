import random
import os
import logging
from datetime import datetime

import system
import reputation as rep
import behavior as beh




def simulate():

    reputation_strategy = rep.ReputationWeightedAverage()
    #reputation_strategy = rep.ReputationAverageStrategy()

    sys = system.System( reputation_strategy )

    aging = rep.Aging()
    weights = rep.Weights()
    stakes = rep.StakeBasedReputation()
    aging.set_next(weights).set_next(stakes)

    sys.improvement_handler = aging

    seed = 10#random.random()
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

        return simulation_dir_path

def setup_logging(logfile_dir):
        logfile_path = os.path.join( logfile_dir, "simulation.log" )

        file_handler = logging.FileHandler(logfile_path)
        stream_handler = logging.StreamHandler()

        logging.basicConfig(
            handlers=[file_handler, stream_handler], 
            datefmt="%H:%M:%S",
            format="%(asctime)s,%(msecs)03d %(levelname)s: [%(filename)s > %(funcName)s()] %(message)s",
            level=logging.DEBUG)            




if __name__ == "__main__":
    simulation_dir_path = prepare_for_artifacts()
    setup_logging(simulation_dir_path)
    simulate()