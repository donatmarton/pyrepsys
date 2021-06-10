import os
import logging
import datetime
import time

from config import configurator as config
import system
import results_processor as reproc
import paths
import helpers

logger = logging.getLogger(helpers.APP_NAME)

def simulate(artifacts_directory, default_config, scenarios):
    starttime = time.process_time()

    logger.info("Simulation started")
    logger.info("Artifact directory is at '{}'".format(artifacts_directory))
    logger.info("Scenarios planned: {}".format(scenarios))

    sys = system.System()
    results_processor = reproc.ResultsProcessor(artifacts_directory)
    sys.results_processor = results_processor
    config.read_default_configuration(default_config)

    for scenario in scenarios:
        logger.info("Beginning scenario: '{}'".format(scenario))

        config.read_configuration(scenario)
        config.configure_system(sys)
        config.configure_results_processor(results_processor)

        scenario_display_name = config.get("scenario_name")
        seed = config.get("seed")

        results_processor.process(
            helpers.SimulationEvent.BEGIN_SCENARIO,
            scenario=scenario_display_name)

        sys.simulate(seed)
        sys.show()

        results_processor.process(
            helpers.SimulationEvent.END_OF_SCENARIO,
            agents_data=sys.agents,
            scenario=scenario_display_name)

        logger.info("Scenario '{}' finished".format(scenario))
        sys.reset_system()
        config.reset_active_configuration()

    results_processor.process(helpers.SimulationEvent.END_OF_SIMULATION)
    logger.info("Simulation finished")

    endtime = time.process_time()
    d = datetime.timedelta(seconds=endtime - starttime)
    logger.info("Simulation process time: " + str(d).split(".")[0])

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

def setup_logging(logfile_dir, default_level, module_levels=None):
        logfile_path = os.path.join( logfile_dir, "simulation.log" )

        file_formatter = logging.Formatter(
            fmt="%(asctime)s,%(msecs)03d %(levelname)s: [%(name)s > %(funcName)s()] %(message)s",
            datefmt="%H:%M:%S")
        stream_formatter = logging.Formatter(
            fmt="%(levelname)s: %(message)s",
            datefmt="%M:%S"
        )

        file_handler = logging.FileHandler(logfile_path)
        file_handler.setFormatter(file_formatter)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(stream_formatter)
        
        root_logger = logging.getLogger()
        root_logger.addHandler(stream_handler)
        root_logger.addHandler(file_handler)

        logger.setLevel(default_level)

        if module_levels:
            for module_name, module_level in module_levels.items():
                module_logger = logging.getLogger(helpers.APP_NAME + "." + module_name)
                module_logger.setLevel(module_level)


if __name__ == "__main__":
    default_level = logging.INFO
    module_levels = {
        #"system": logging.DEBUG,
        #"metrics": logging.DEBUG
    } # a module will remain on default if not overwritten here
    default_config_name = "default_config.yaml"
    scenarios = [
        "config.yaml",
        "alt_config.yaml"
    ]
    
    simulation_dir_path = prepare_artifacts_directory()
    setup_logging(simulation_dir_path, default_level, module_levels)
    simulate(simulation_dir_path, default_config_name, scenarios)