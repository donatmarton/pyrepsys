import os
import logging
import datetime
import time

from config import configurator as config
import system
import results_processor as reproc
import paths
import helpers




def simulate(artifacts_directory, default_config, scenarios):
    logging.info("Simulation started")
    logging.info("Scenarios planned: {}".format(scenarios))

    sys = system.System()
    results_processor = reproc.ResultsProcessor(artifacts_directory)
    sys.results_processor = results_processor
    config.read_default_configuration(default_config)

    for scenario in scenarios:
        logging.info("Beginning scenario: '{}'".format(scenario))

        config.read_configuration(scenario)
        config.configure_system(sys)
        config.configure_results_processor(results_processor)

        scenario_display_name = config.get("scenario_name")
        seed = config.get("seed")

        results_processor.process(
            helpers.SimulationEvent.BEGIN_SCENARIO,
            scenario=scenario_display_name)

        sys.simulate(seed)
        #sys.show()

        results_processor.process(
            helpers.SimulationEvent.END_OF_SCENARIO,
            agents_data=sys.agents,
            scenario=scenario_display_name)

        sys.reset_system()
        config.reset_active_configuration()

    results_processor.process(helpers.SimulationEvent.END_OF_SIMULATION)
    logging.info("Simulation finished")

def prepare_artifacts_directory():
        now = datetime.datetime.now()
        # create sim dir name: run_YYYY-MM-DD_HH:MM:SS
        simulation_dir_name = now.strftime( "run_%Y-%m-%d_%H:%M:%S" )
        simulation_dir_path = os.path.abspath(
            os.path.join( paths.simulation_artifacts_path, simulation_dir_name ))
        
        os.makedirs(simulation_dir_path, exist_ok=True)

        symlink = os.path.join( paths.simulation_artifacts_path, "run_latest" )
        try:
            os.remove(symlink)
        except FileNotFoundError:
            pass
        os.symlink(simulation_dir_path, symlink, target_is_directory=True)

        return simulation_dir_path

def setup_logging(logfile_dir, level):
        logfile_path = os.path.join( logfile_dir, "simulation.log" )

        file_handler = logging.FileHandler(logfile_path)
        stream_handler = logging.StreamHandler()

        logging.basicConfig(
            handlers=[file_handler, stream_handler], 
            datefmt="%H:%M:%S",
            format="%(asctime)s,%(msecs)03d %(levelname)s: [%(filename)s > %(funcName)s()] %(message)s",
            level=level)

        # there is a bug where matplotlib font_manager debug logs appear regardless of global level
        # disable these debug logs as per suggestion here:
        # https://stackoverflow.com/questions/58320567/matplotlib-font-manager-debug-messages-in-log-file#58342614
        logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)



if __name__ == "__main__":
    simulation_dir_path = prepare_artifacts_directory()
    setup_logging(simulation_dir_path, logging.DEBUG)
    logging.info("Artifact directory is at '{}'".format(simulation_dir_path))

    default_config_name = "default_config.yaml"
    scenarios = [
        "config.yaml",
        "alt_config.yaml"
    ]

    starttime = time.process_time()
    simulate(simulation_dir_path, default_config_name, scenarios)
    endtime = time.process_time()
    d = datetime.timedelta(seconds=endtime - starttime)
    logging.info("Simulation process time: " + str(d).split(".")[0])