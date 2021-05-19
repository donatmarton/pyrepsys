import random
import os
import logging
from datetime import datetime

from config import configurator as config
import system
import paths




def simulate(default_config, scenarios):
    logging.info("Simulation started")
    logging.info("Scenarios planned: {}".format(scenarios))

    sys = system.System()
    config.read_default_configuration(default_config)

    for scenario in scenarios:
        logging.info("Beginning scenario: '{}'".format(scenario))

        config.read_configuration(scenario)
        seed = config.configure_system(sys)

        sys.simulate(seed)
        #sys.show()

        sys.reset_system()
    
    logging.info("Simulation finished")

def prepare_for_artifacts():
        now = datetime.now()
        # create sim dir name: run_YYYY-MM-DD_HH:MM:SS
        simulation_dir_name = now.strftime( "run_%Y-%m-%d_%H:%M:%S" )
        simulation_dir_path = os.path.join( paths.simulation_artifacts_path, simulation_dir_name )
        
        os.makedirs(simulation_dir_path, exist_ok=True)

        symlink = os.path.join( paths.simulation_artifacts_path, "run_latest" )
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

    default_config_name = "default_config.yaml"
    scenarios = [
        "config.yaml",
        "alt_config.yaml"
    ]
    simulate(default_config_name, scenarios)