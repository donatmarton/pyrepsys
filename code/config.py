import os
import logging

import yaml

import paths
import reputation as rep
import behavior as beh


class Configurator:
    def __init__(self):
        self._default_config = {}
        self._active_config = {}

    def read_configuration(self, config_file_name):
        self._active_config = self._config_from_file_to_memory(config_file_name)

    def read_default_configuration(self, default_config_file_name):
        self._default_config = self._config_from_file_to_memory(default_config_file_name)

    def _config_from_file_to_memory(self, config_file_name):
        config_file_path = os.path.join(paths.config_files_path, config_file_name)
        with open(config_file_path, 'r') as file:
            dictionary = yaml.safe_load(file)
        return dictionary

    def get(self, config_name, allow_default=True):
        try:
            cfg_value = self._active_config[config_name]
        except KeyError:
            if allow_default:
                try:
                    logging.warning(
                        "'{}' not in active config, fetching from default config instead".format(config_name))
                    cfg_value = self._default_config[config_name]
                except KeyError:
                    logging.error("'{}' is not part of the default config".format(config_name))
                    raise
            else:
                logging.error("'{}' not in active config and defaulting is not allowed".format(config_name))
                raise
        return cfg_value

    def configure_system(self, system):
        logging.info("Configuring system")

        cfg_reputation_strategy = self.get("reputation_strategy")
        reputation_strategy = getattr(rep,cfg_reputation_strategy)()
        system.reputation_strategy = reputation_strategy

        cfg_improvement_handlers = self.get("improvement_handlers")
        assert len(cfg_improvement_handlers) > 0
        improvement_handlers = []
        for cfg_handler in cfg_improvement_handlers:
            handler = getattr(rep, cfg_handler)()
            improvement_handlers.append(handler)
        for i, handler in enumerate(improvement_handlers):
            if i < len(improvement_handlers)-1:
                handler.set_next(improvement_handlers[i+1])
        logging.info("Handler chain found: {}".format(
            "".join([h + " > " for h in cfg_improvement_handlers])
        ))
        system.improvement_handler = improvement_handlers[0]

        agents = self.get("agents")
        for agent in agents:
            amount = agent["amount"]
            assert type(amount) is int
            cfg_rate_strategy = agent["rate_strategy"]
            cfg_distort_strategy = agent["distort_strategy"]
            ds = getattr(beh,cfg_distort_strategy)()
            rs = getattr(beh,cfg_rate_strategy)()
            system.create_agents(rs, ds, amount)

        seed = self.get("seed")
        return seed

configurator = Configurator()

class DefaultConfig:
    NUM_AGENTS=100
    NUM_MAX_RATERS=10

    MIN_RATING = 1
    MAX_RATING = 9
    DECIMAL_PRECISION = 0 # 0 for int

    INITIAL_REPUTATION = 5 # in user-facing range and precision

    MEASUREMENT_ERROR = 0.1 # in internal 0..1 range

    SIM_ROUND_MAX = 5
    SIM_ROUND_MIN = 1

    AGING_LIMIT = 2
    # 0 to only allow from current round, 1 to allow from one before too ...

