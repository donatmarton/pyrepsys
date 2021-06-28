import os
import logging

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
        self._active_config = self._config_from_file_to_memory(config_file_name)
        self._notify_update()

    def read_default_configuration(self, default_config_file_name):
        self._default_config = self._config_from_file_to_memory(default_config_file_name)
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
            dictionary = yaml.safe_load(file)
        dictionary["scenario_name"] = config_file_name.split(sep=".", maxsplit=1)[0]
        return dictionary

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
            for metric_cfg in metrics_cfg:
                if not results_processor.has_metric(metric_cfg):
                    metric = self.instantiator.create_metric(metric_cfg)
                    logger.debug("Created metric '{}'".format(metric))
                    results_processor.add_metric(metric)
                results_processor.activate_metric(metric_cfg)
        logger.info("Enabled metrics: {}".format(metrics_cfg))           

    def configure_system(self, system):
        logger.debug("Configuring system")

        cfg_reputation_strategy = self.get("reputation_strategy")
        reputation_strategy = self.instantiator.create_reputation_strategy(cfg_reputation_strategy)
        system.reputation_strategy = reputation_strategy

        cfg_improvement_handlers = self.get("improvement_handlers")
        if cfg_improvement_handlers is not None:
            improvement_handlers = []
            for cfg_handler in cfg_improvement_handlers:
                handler = self.instantiator.create_improvement_handler(cfg_handler)
                improvement_handlers.append(handler)
            for i, handler in enumerate(improvement_handlers):
                if i < len(improvement_handlers)-1:
                    handler.set_next(improvement_handlers[i+1])
            logger.info("Improvement handler chain found: {}".format(
                " > ".join([h for h in cfg_improvement_handlers])
            ))
            system.improvement_handler = improvement_handlers[0]
        else:
            logger.warning("No improvement handler chain found")
            system.improvement_handler = None

        agents = self.get("agents")
        agent_base_behaviors = self.get("agent_base_behaviors")
        for agent in agents:
            try:
                cfg_base_behavior = agent["base_behavior"]
            except KeyError: # no base behavior was given
                base_behavior = None
            else: # get the base behavior, KeyError shows config error (not catched)
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
                            raise ConfigurationError("missing parameter '{}' must be defined".format(cfg_param_key))
                return cfg_param_value

            amount = agent["amount"] # can't be defined as base behavior
            if type(amount) is not int or amount <= 0:
                raise ConfigurationError("'amount' must be an integer > 0")
            cfg_rate_strategy = fetch_agent_cfg_entry("rate_strategy")
            cfg_distort_strategy = fetch_agent_cfg_entry("distort_strategy")
            ds = self.instantiator.create_distort_strategy(cfg_distort_strategy)
            rs = self.instantiator.create_rating_strategy(cfg_rate_strategy)
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

_configurator = None
def getConfigurator():
    global _configurator
    if not _configurator: 
        _configurator = Configurator()
    return _configurator