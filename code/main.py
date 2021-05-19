import random
import os
import logging
from datetime import datetime

import yaml

import system
import reputation as rep
import behavior as beh
import helpers




def simulate(scenarios):
    
    sys = system.System()

    for scenario in scenarios:
        logging.info("Beginning new scenario: '{}'".format(scenario))

        seed = configure_system(sys, scenario)

        sys.simulate(seed)
        #sys.show()

        sys.reset_system()

def prepare_for_artifacts():
        now = datetime.now()
        # create sim dir name: run_YYYY-MM-DD_HH:MM:SS
        simulation_dir_name = now.strftime( "run_%Y-%m-%d_%H:%M:%S" )
        simulation_dir_path = os.path.join( helpers.simulation_artifacts_path, simulation_dir_name )
        
        os.makedirs(simulation_dir_path, exist_ok=True)

        symlink = os.path.join( helpers.simulation_artifacts_path, "run_latest" )
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

def configure_system(system, config_file_name):
    logging.info("Configuring from '{}'".format(config_file_name))

    config_file_path = os.path.join(helpers.config_files_path, config_file_name)
    with open(config_file_path, 'r') as file:
        config_root = yaml.safe_load(file)    

    cfg_reputation_strategy = config_root["reputation_strategy"]
    reputation_strategy = getattr(rep,cfg_reputation_strategy)()
    system.reputation_strategy = reputation_strategy

    cfg_improvement_handlers = config_root["improvement_handlers"]
    assert len(cfg_improvement_handlers) > 0
    improvement_handlers = []
    for cfg_handler in cfg_improvement_handlers:
        handler = getattr(rep, cfg_handler)()
        improvement_handlers.append(handler)
    for i, handler in enumerate(improvement_handlers):
        if i < len(improvement_handlers)-1:
            handler.set_next(improvement_handlers[i+1])
    system.improvement_handler = improvement_handlers[0]

    agents = config_root["agents"]
    for agent in agents:
        amount = agent["amount"]
        assert type(amount) is int
        cfg_rate_strategy = agent["rate_strategy"]
        cfg_distort_strategy = agent["distort_strategy"]
        ds = getattr(beh,cfg_distort_strategy)()
        rs = getattr(beh,cfg_rate_strategy)()
        system.create_agents(rs, ds, amount)

    seed = config_root["seed"]
    return seed




if __name__ == "__main__":
    simulation_dir_path = prepare_for_artifacts()
    setup_logging(simulation_dir_path)

    scenarios = [
        "config.yaml",
        "alt_config.yaml"
    ]
    simulate(scenarios)