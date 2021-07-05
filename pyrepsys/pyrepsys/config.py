import os
import logging
import hashlib

import yaml

from pyrepsys.helper_types import ClaimLimits
from pyrepsys.errors import ConfigurationError, UncompleteInitializationError

logger = logging.getLogger(__name__)

class Configurator:
    def __init__(self, instantiator=None):
        self.instantiator = instantiator
        self._default_config = {}
        self._active_config = {}
        self.was_defaulted = False
        self.scenarios_dir = None
        self._update_callbacks = []

    def read_configuration(self, config_file_name):
        if self._active_config:
            logger.warning("Overwriting not empty active configuration, is this ok?")
        self._active_config, filehash = self._config_from_file_to_memory(config_file_name)
        logger.info("Scenario file hash: '{}'".format(filehash))
        self._notify_update()

    def read_default_configuration(self, default_config_file_name):
        self._default_config, filehash = self._config_from_file_to_memory(default_config_file_name)
        logger.info("Scenario defaults file hash: '{}'".format(filehash))
        self._notify_update()

    def reset_active_configuration(self):
        self._active_config = {}
        self._notify_update()
        if self.was_defaulted:
            logger.warning("Configurator has defaulted at least one parameter since last active reset, is this ok?")
            self.was_defaulted = False

    def register_config_updated_callback(self, callable):
        if callable not in self._update_callbacks:
            self._update_callbacks.append(callable)

    def _notify_update(self):
        for callable in self._update_callbacks:
            callable()

    def _config_from_file_to_memory(self, config_file_name):
        if self.scenarios_dir is not None:
            config_file_path = os.path.join(self.scenarios_dir, config_file_name)
        else:
            raise UncompleteInitializationError
        
        with open(config_file_path, 'r') as file:
            config_file_contents = file.read()

        dictionary = yaml.safe_load(config_file_contents)
        dictionary["scenario_name"] = config_file_name.split(sep=".", maxsplit=1)[0]

        sha256 = hashlib.sha256(config_file_contents.encode("utf-8"))
        filehash = sha256.hexdigest()
        
        return dictionary, filehash

    def get(self, config_name):
        try:
            cfg_value = self._active_config[config_name]
        except KeyError:
            try:
                cfg_value = self._default_config[config_name]
                self.was_defaulted = True
            except KeyError:
                logger.error("'{}' is not part of the active or default config".format(config_name))
                raise
        return cfg_value

    def configure_results_processor(self, results_processor):
        metrics_cfg = self.get("metrics")
        results_processor.deactivate_all_metrics()
        if metrics_cfg is not None:
            metric_names, metric_configs = self._unpack_extended_config_list(metrics_cfg)
            for name in metric_names:
                if not results_processor.has_metric(name):
                    metric = self.instantiator.create_metric(name)
                    logger.debug("Created metric '{}'".format(metric))
                    metric.local_config = metric_configs.get(name)
                    results_processor.add_metric(metric)
                elif results_processor.has_metric(name) and name in metric_configs:
                    logger.warning("metric '{}' has configs but was already instantiated earlier, configs have no effect".format(name))
                results_processor.activate_metric(name)
            logger.info("Enabled metrics: {}".format(metric_names))           
        else: logger.info("No metrics enabled")

    def configure_system(self, system):
        logger.debug("Configuring system")

        self._configure_system_reputation_strategy(system)
        self._configure_system_improvement_handlers(system)
        self._configure_system_agents(system)

    def _configure_system_reputation_strategy(self, system):
        cfg_reputation_strategy = self.get("reputation_strategy")
        if cfg_reputation_strategy is not None:
            rs_name, rs_config = self._unpack_extended_config_entry(cfg_reputation_strategy)
            reputation_strategy = self.instantiator.create_reputation_strategy(rs_name)
            reputation_strategy.local_config = rs_config
            system.reputation_strategy = reputation_strategy
        else:
            raise ConfigurationError("no reputation strategy found")

    def _configure_system_improvement_handlers(self, system):
        cfg_improvement_handlers = self.get("improvement_handlers")
        if cfg_improvement_handlers is not None:
            handler_names, handler_configs = self._unpack_extended_config_list(cfg_improvement_handlers)
            improvement_handlers = []
            for name in handler_names:
                handler = self.instantiator.create_improvement_handler(name)
                handler.local_config = handler_configs.get(name)
                improvement_handlers.append(handler)
            for idx, handler in enumerate(improvement_handlers):
                if idx < len(improvement_handlers)-1:
                    handler.set_next(improvement_handlers[idx+1])
            logger.info("Improvement handler chain found: {}".format(
                " > ".join([h for h in handler_names])
            ))
            system.improvement_handler = improvement_handlers[0]
        else:
            logger.warning("No improvement handler chain found")
            system.improvement_handler = None

    def _configure_system_agents(self, system):
        agents = self.get("agents")
        agent_base_behaviors = self.get("agent_base_behaviors")
        for agent in agents:
            try:
                cfg_base_behavior = agent["base_behavior"]
            except KeyError: # no base behavior was given
                base_behavior = None
            else: # get the base behavior, raise config error if missing
                base_behavior = None
                for bb in agent_base_behaviors:
                    if bb["name"] == cfg_base_behavior:
                        base_behavior = bb
                if base_behavior is None:
                    raise ConfigurationError("can't find base behavior with name '{}'".format(cfg_base_behavior))

            def fetch_agent_cfg_entry(cfg_param_key):
                try:
                    cfg_param_value = agent[cfg_param_key]
                except KeyError:
                    if base_behavior:
                        try:
                            cfg_param_value = base_behavior[cfg_param_key]
                        except KeyError:
                            raise ConfigurationError("missing parameter '{}' must be defined, not in agent or base behavior".format(cfg_param_key))
                    else: raise ConfigurationError("missing parameter '{}' must be defined, not in agent and no base behavior given".format(cfg_param_key))
                return cfg_param_value

            amount = agent["amount"] # can't be defined as base behavior
            if type(amount) is not int or amount <= 0:
                raise ConfigurationError("'amount' must be an integer > 0")
            cfg_rate_strategy = fetch_agent_cfg_entry("rate_strategy")
            cfg_distort_strategy = fetch_agent_cfg_entry("distort_strategy")
            ds_name, ds_config = self._unpack_extended_config_entry(cfg_distort_strategy)
            ds = self.instantiator.create_distort_strategy(ds_name)
            ds.local_config = ds_config
            rs_name, rs_config = self._unpack_extended_config_entry(cfg_rate_strategy)
            rs = self.instantiator.create_rating_strategy(rs_name)
            rs.local_config = rs_config
            claim_probability = fetch_agent_cfg_entry("claim_probability")
            rate_probability = fetch_agent_cfg_entry("rate_probability")
            claim_range = fetch_agent_cfg_entry("claim_range")
            if len(claim_range) != 2:
                raise ConfigurationError("incorrect 'claim_range'")
            min_claim = claim_range[0]
            max_claim = claim_range[1]
            if not (min_claim <= 1 and min_claim >= 0) or \
                not (max_claim <= 1 and max_claim >= 0):
                raise ConfigurationError("min and max claim must be within 0..1")
            if min_claim > max_claim:
                raise ConfigurationError("'min_claim' can't be larger than 'max_claim'")
            claim_limits = ClaimLimits(min=min_claim, max=max_claim)
            claim_truth_assessment_inaccuracy = fetch_agent_cfg_entry("claim_truth_assessment_inaccuracy")
            system.create_agents(
                ds, 
                rs, 
                claim_limits, 
                claim_probability, 
                rate_probability,
                claim_truth_assessment_inaccuracy, 
                amount)

    def _unpack_extended_config_list(self, config_entries_list):
        names_in_list = []
        configs = {}
        for entry in config_entries_list:
            if type(entry) is str:
                names_in_list.append(entry)
            else:
                try: name = entry["name"]
                except KeyError: raise ConfigurationError("config item extended with settings but no 'name' param")
                else:
                    names_in_list.append(name)
                    configs[name] = entry
        return names_in_list, configs

    def _unpack_extended_config_entry(self, config_entry):
        name_in_list, config_in_dict = self._unpack_extended_config_list( [config_entry] )
        name = name_in_list[0]
        config = config_in_dict.get(name)
        return name, config




_configurator = None
def getConfigurator():
    global _configurator
    if not _configurator: 
        _configurator = Configurator()
    return _configurator