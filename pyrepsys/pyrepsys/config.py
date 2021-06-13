import os
import logging

import yaml

import pyrepsys.paths as paths
import pyrepsys.reputation as rep
import pyrepsys.behavior as beh
import pyrepsys.helpers as helpers

logger = logging.getLogger(__name__)

class Configurator:
    def __init__(self):
        self._default_config = {}
        self._active_config = {}
        self.was_defaulted = False
        self.scenarios_dir = None

    def read_configuration(self, config_file_name):
        if self._active_config:
            logger.warning("Overwriting not empty active configuration, is this ok?")
        self._active_config = self._config_from_file_to_memory(config_file_name)

    def read_default_configuration(self, default_config_file_name):
        self._default_config = self._config_from_file_to_memory(default_config_file_name)

    def reset_active_configuration(self):
        self._active_config = {}
        if self.was_defaulted:
            logger.warning("Configurator has defaulted at least one parameter since last active reset, is this ok?")
            self.was_defaulted = False


    def _config_from_file_to_memory(self, config_file_name):
        if self.scenarios_dir is not None:
            config_file_path = os.path.join(self.scenarios_dir, config_file_name)
        else:
            raise helpers.UncompleteInitializationError
        
        with open(config_file_path, 'r') as file:
            dictionary = yaml.safe_load(file)
        dictionary["scenario_name"] = config_file_name.split(sep=".", maxsplit=1)[0]
        return dictionary

    def get(self, config_name, allow_default=True):
        try:
            cfg_value = self._active_config[config_name]
        except KeyError:
            if allow_default:
                try:
                    cfg_value = self._default_config[config_name]
                    self.was_defaulted = True
                except KeyError:
                    logger.error("'{}' is not part of the active or default config".format(config_name))
                    raise
            else:
                logger.error("'{}' not in active config and defaulting is not allowed".format(config_name))
                raise
        return cfg_value

    def configure_results_processor(self, results_processor):
        metrics_cfg = self.get("metrics")
        results_processor.deactivate_all_metrics()

        if metrics_cfg is not None:
            for metric_cfg in metrics_cfg:
                results_processor.activate_metric(metric_cfg)
        logger.info("Enabled metrics: {}".format(metrics_cfg))           

    def configure_system(self, system):
        logger.debug("Configuring system")

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
        logger.info("Handler chain found: {}".format(
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
            claim_probability = agent["claim_probability"]
            rate_probability = agent["rate_probability"]
            claim_range = agent["claim_range"]
            assert len(claim_range) == 2
            claim_limits = helpers.ClaimLimits(min=claim_range[0], max=claim_range[1])
            claim_truth_assessment_inaccuracy = agent["claim_truth_assessment_inaccuracy"]
            system.create_agents(
                ds, 
                rs, 
                claim_limits, 
                claim_probability, 
                rate_probability,
                claim_truth_assessment_inaccuracy, 
                amount)

configurator = Configurator()
get = configurator.get