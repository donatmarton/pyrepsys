import bisect

import pyrepsys.config
from pyrepsys.errors import ConfigurationError
from pyrepsys.helper_types import ResolutionDomain

config = pyrepsys.config.getConfigurator()

current_sim_round = 0
measured_claim_steps = None
review_steps = None

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

def _configure_system_resolutions():
    def generate_resolution_steps(min, max, step_size):
        span = max - min
        if dumb_mod(span, step_size) != 0:
            raise ConfigurationError("resolutions must be divisor of their range spans (max-min)")
        num_steps = int(1 + span / step_size)
        return [min + idx*step_size for idx in range(num_steps)]

    min_rating = config.get("MIN_RATING")
    max_rating = config.get("MAX_RATING")
    if min_rating > max_rating:
        raise ConfigurationError("'min_rating' can't be larger than 'max_rating'")
    if min_rating == max_rating:
        raise ConfigurationError("rating span (max-min) can't be 0")

    measured_claim_resolution = config.get("MEASURED_CLAIM_RESOLUTION")
    global measured_claim_steps
    measured_claim_steps = generate_resolution_steps(
        min_rating, 
        max_rating, 
        measured_claim_resolution
    )
    review_resolution = config.get("REVIEW_RESOLUTION")
    global review_steps
    review_steps = generate_resolution_steps(
        min_rating, 
        max_rating, 
        review_resolution
    )
config.register_config_updated_callback(_configure_system_resolutions)

def convert_resolution(number, target_resolution_domain):
    if target_resolution_domain is ResolutionDomain.MEASURED_CLAIM:
        return find_nearest_step(number, measured_claim_steps)
    elif target_resolution_domain is ResolutionDomain.REVIEW:
        return find_nearest_step(number, review_steps)
    else:
        raise NotImplementedError

def find_nearest_step(number, steps_sorted_list):
    i = bisect.bisect_left(steps_sorted_list, number)

    if number < steps_sorted_list[0] or number > steps_sorted_list[-1]:
        raise ValueError

    if steps_sorted_list[i] == number:
        return steps_sorted_list[i]
    else:
        diff_left = round(abs( steps_sorted_list[i-1] - number ), 8)
        diff_right = round(abs( steps_sorted_list[i] - number ), 8)
        if diff_left < diff_right: return steps_sorted_list[i-1]
        else: return steps_sorted_list[i]

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

def dumb_mod(x, y):
    """
    aka the best modulo. More precise with small y values (e.g. 0.01). Only for positive inputs!
    """
    remain = x
    while remain > 0:
        remain -= y
    if remain < 0: remain+=y
    return round(remain,8)
