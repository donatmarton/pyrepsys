import logging
import os
from copy import deepcopy
import re

import yaml

import pyrepsys.paths as paths
from pyrepsys.helpers import ConfigurationError
from pyrepsys.main import setup_logging

logger = logging.getLogger(__name__)

# TODO logging needs to be fixed, displays twice now, called twice to setup
# TODO runparams_file needs to go also as argument

def run_scenario_creator(generator, scenario_defaults=None):
    runparams_file = "run_params.yaml"

    setup_logging(logging.INFO)

    logger.debug("Using '{}' for parameter variants".format(generator))

    created_scenarios = create_scenarios(generator)
    write_runparams(runparams_file, scenario_defaults, created_scenarios)

    logger.info("Scenario creation finished")

def clean_generated_scenarios():
    setup_logging(logging.INFO)
    scenarios_dir = paths.scenarios_dir

    num_cleaned = 0
    pattern = re.compile("sc_.*[.]yaml")
    for file in os.listdir(scenarios_dir):
        if re.search(pattern, file):
            os.remove(os.path.join(scenarios_dir, file))
            num_cleaned += 1
    
    logger.info("Cleaned {} scenarios".format(num_cleaned))


def create_scenarios(generator_file_name):
    scenarios_dir = paths.scenarios_dir

    generator_path = os.path.join(scenarios_dir, generator_file_name)
    with open(generator_path, 'r') as file:
        generator_dict = yaml.safe_load(file)

    if generator_dict is None:
        raise ConfigurationError("parameter variants file found empty")
    if len(generator_dict) < 2:
        raise ConfigurationError("at least 2 parameters should be given to create combinations")

    all_combinations = []
    for param, variants_list in generator_dict.items():
        if variants_list is None:
            logger.error("No variants found for '{}', skipping this parameter".format(param))
            continue
        if len(variants_list) == 1:
            logger.warning("Found only 1 variant for '{}', which doesn't make much sense.. continuing".format(param))
        if all_combinations: # some combis are already there, expand them
            previos_combinations = deepcopy(all_combinations)
            all_combinations = []
            for i, variant in enumerate(variants_list):
                new_combinations = deepcopy(previos_combinations)
                for combination in new_combinations:
                    combination[param] = variant
                    combination["id"] = combination["id"] + str(i)
                    all_combinations.append(combination)
        else: # no combinations yet
            for i, variant in enumerate(variants_list):
                all_combinations.append( {param: variant, "id": str(i)} )

    generated_scenarios = []
    for c in all_combinations:
        id_str = c.pop("id")
        scenario_file_name = "sc_" + id_str + ".yaml"
        scenario_path = os.path.join(scenarios_dir, scenario_file_name)
        if os.path.exists(scenario_path):
            logger.warning("A scenario named '{}' already exists, overwriting".format(scenario_file_name))
        with open(scenario_path, 'w', encoding = "utf-8") as file:
            yaml.dump(c, file, default_flow_style=False)
        generated_scenarios.append(scenario_file_name)

    logger.info("{} scenarios created".format(len(generated_scenarios)))
    return generated_scenarios

def write_runparams(runparams_file_name, scenario_defaults, scenarios_list):
    runparams = {}
    runparams["scenario_defaults"] = scenario_defaults
    runparams["scenarios"] = scenarios_list

    runparams_file_path = os.path.join(paths.run_params_dir, runparams_file_name)
    if os.path.exists(runparams_file_path):
        logger.warning("A runparams file named '{}' already exists, overwriting".format(runparams_file_name))
    with open(runparams_file_path, 'w') as file:
        yaml.dump(runparams, file, default_flow_style=False)

    logger.debug("Scenarios written to runparams file: '{}'".format(runparams_file_path))