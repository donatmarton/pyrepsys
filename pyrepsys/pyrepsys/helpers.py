import pyrepsys.config

config = pyrepsys.config.getConfigurator()


current_sim_round = 0

_config_cache = {
    "MIN_RATING": None,
    "MAX_RATING": None,
    "DECIMAL_PRECISION": None,
    "MAX_MIN_RATING_SPAN": None
}
def update_config_cache():
    _config_cache["MIN_RATING"] = config.get("MIN_RATING")
    _config_cache["MAX_RATING"] = config.get("MAX_RATING")
    _config_cache["DECIMAL_PRECISION"] = config.get("DECIMAL_PRECISION")
    _config_cache["MAX_MIN_RATING_SPAN"] = _config_cache["MAX_RATING"] - _config_cache["MIN_RATING"]
config.register_config_updated_callback(update_config_cache)

def force_agent_exposed_bounds(score):
    return max( min(score, _config_cache["MAX_RATING"]), _config_cache["MIN_RATING"])

def force_internal_bounds(score):
    return max( min(score, 1), 0)

def internal_to_agent(score):
    """
    Transforms an internal score from [0..1] to agent-exposed score
    """
    num_decimals = _config_cache["DECIMAL_PRECISION"]

    value_in_range = _config_cache["MIN_RATING"] + (_config_cache["MAX_MIN_RATING_SPAN"]) * score
    rounded_in_range = round(value_in_range, num_decimals)
    return int(rounded_in_range) if num_decimals == 0 else rounded_in_range
i2a = internal_to_agent

def agent_to_internal(score):
    """
    Transforms an agent-exposed score into internal
    """
    return (score - _config_cache["MIN_RATING"]) / (_config_cache["MAX_MIN_RATING_SPAN"])
a2i= agent_to_internal

def is_within_internal_bounds(score):
    return score <= 1 and score >= 0