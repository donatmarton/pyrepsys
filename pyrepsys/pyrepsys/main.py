import os
import logging
import datetime
import time

import yaml

import pyrepsys.instantiator as instantiator
import pyrepsys.config as config
import pyrepsys.scenario_simulator as scenario_simulator
import pyrepsys.results_processor as reproc
import pyrepsys.paths as paths
from pyrepsys.helper_types import SimulationEvent
from pyrepsys.errors import ConfigurationError

logger = logging.getLogger(__name__)

def simulate(default_scenario, scenarios, artifacts_dir):
    starttime = time.process_time()

    logger.info("Simulation started")
    logger.info("Artifacts will be saved to '{}'".format(artifacts_dir))
    logger.info("Scenarios will be read from '{}'".format(paths.scenarios_dir))
    logger.info("Scenarios planned: {}".format(scenarios))
    logger.info("Fallback scenario defaults: '{}'".format(default_scenario))

    sys = scenario_simulator.ScenarioSimulator()
    results_processor = reproc.ResultsProcessor(artifacts_dir)
    sys.results_processor = results_processor
    configurator = config.getConfigurator()
    configurator.scenarios_dir = paths.scenarios_dir
    configurator.instantiator = instantiator.Instantiator()
    configurator.read_default_configuration(default_scenario)

    for scenario in scenarios:
        logger.info("Beginning scenario: '{}'".format(scenario))

        configurator.read_configuration(scenario)
        configurator.configure_system(sys)
        configurator.configure_results_processor(results_processor)

        scenario_display_name = configurator.get("scenario_name")
        seed = configurator.get("seed")

        results_processor.process(
            SimulationEvent.BEGIN_SCENARIO,
            scenario=scenario_display_name)

        sys.simulate(seed)
        sys.show()

        results_processor.process(
            SimulationEvent.END_OF_SCENARIO,
            agents_data=sys.agents,
            scenario=scenario_display_name)

        logger.info("Scenario '{}' finished".format(scenario))
        sys.reset_system()
        configurator.reset_active_configuration()

    results_processor.process(SimulationEvent.END_OF_SIMULATION)
    logger.info("Simulation finished")

    endtime = time.process_time()
    d = datetime.timedelta(seconds=endtime - starttime)
    logger.info("Total simulation process time: " + str(d).split(".")[0])

def prepare_artifacts_directory():
        now = datetime.datetime.now()
        # create sim dir name: run_YYYY-MM-DD_HH:MM:SS
        simulation_dir_name = now.strftime( "run_%Y-%m-%d_%H:%M:%S" )
        simulation_dir_path = os.path.abspath(
            os.path.join( paths.simulation_artifacts_path, simulation_dir_name ))
        
        try:
            os.makedirs(simulation_dir_path, exist_ok=False)
        except FileExistsError:
            success = False
            count = 1
            while not success:
                alt_sim_dir = simulation_dir_path + " ({})".format(count)
                try: 
                    os.makedirs(alt_sim_dir, exist_ok=False)
                except FileExistsError:
                    count += 1
                else:
                    success = True
                    simulation_dir_path = alt_sim_dir

        symlink = os.path.join( paths.simulation_artifacts_path, "run_latest" )
        try:
            os.remove(symlink)
        except FileNotFoundError:
            pass
        os.symlink(simulation_dir_path, symlink, target_is_directory=True)

        return simulation_dir_path

def setup_logging(default_level, logfile_dir=None, module_levels=None):
        app_logger = logging.getLogger("pyrepsys")
        app_logger.setLevel(default_level)

        stream_formatter = logging.Formatter(
            fmt="%(levelname)s: %(message)s",
            datefmt="%M:%S"
        )

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(stream_formatter)
        
        root_logger = logging.getLogger()
        if root_logger.hasHandlers():
            for h in root_logger.handlers:
                root_logger.removeHandler(h)
        root_logger.addHandler(stream_handler)
        
        if logfile_dir:
            logfile_path = os.path.join( logfile_dir, "simulation.log" )
            file_formatter = logging.Formatter(
                fmt="%(asctime)s,%(msecs)03d %(levelname)s: [%(name)s > %(funcName)s()] %(message)s",
                datefmt="%H:%M:%S")

            file_handler = logging.FileHandler(logfile_path)
            file_handler.setFormatter(file_formatter)

            root_logger.addHandler(file_handler)

        if module_levels:
            for module_name, module_level in module_levels.items():
                module_logger = logging.getLogger("pyrepsys." + module_name)
                module_logger.setLevel(module_level)


def read_scheduled_scenarios(run_params_file_name):
    config_file_path = os.path.join(paths.run_params_dir, run_params_file_name)
    with open(config_file_path, 'r') as file:
        dictionary = yaml.safe_load(file)
    scenarios = dictionary["scenarios"]
    scenario_defaults = dictionary["scenario_defaults"]
    if not scenarios or len(scenarios) == 0:
        raise ConfigurationError("no scenarios found in runparams file")
    return scenarios, scenario_defaults

def set_run_params_dir(path):
    paths.run_params_dir = path

def set_scenarios_dir(path):
    paths.scenarios_dir = path

def set_simulation_artifacts_dir(path):
    paths.simulation_artifacts_path = path

def main(run_params_file_name=None, scenario_list=None, scenario_defaults=None):
    default_level = logging.INFO
    module_levels = {
        #"scenario_simulator": logging.INFO,
        #"metrics": logging.DEBUG
    } # a module will remain on default if not overwritten here

    if run_params_file_name and scenario_list:
        raise TypeError("run_params_file_name and scenario_list were both passed, only one is allowed")
    elif run_params_file_name:
        scenarios, default_config_name = read_scheduled_scenarios(run_params_file_name)
    elif scenario_list:
        if type(scenario_list) is not list:
            raise TypeError("scenario_list must be a list")
        if not scenario_defaults:
            raise TypeError("when giving scenario_list, scenario_defaults also must be provided")
        scenarios = scenario_list
        default_config_name = scenario_defaults
    else:
        raise TypeError("either run_params_file_name or scenario_list with scenario_defaults must be provided")

    simulation_dir_path = prepare_artifacts_directory()
    setup_logging(default_level, simulation_dir_path, module_levels)
    simulate(default_config_name, scenarios, simulation_dir_path)
    return simulation_dir_path

def run_scenario_creator(generator=None, runparams_file_name=None, scenario_defaults=None, clean=False):
    import pyrepsys.scenario_creator
    setup_logging(logging.INFO)
    return pyrepsys.scenario_creator.run_scenario_creator(
        generator=generator,
        runparams_file_name=runparams_file_name,
        scenario_defaults=scenario_defaults,
        clean=clean
    )