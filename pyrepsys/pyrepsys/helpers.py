import pyrepsys.config as config


current_sim_round = 0

def force_agent_exposed_bounds(score):
    min_rating = config.get("MIN_RATING")
    max_rating = config.get("MAX_RATING")
    return max( min(score, max_rating), min_rating)

def force_internal_bounds(score):
    return max( min(score, 1), 0)

def internal_to_agent(score):
    """
    Transforms an internal score from [0..1] to agent-exposed score
    """
    min_val = config.get("MIN_RATING")
    max_val = config.get("MAX_RATING")
    num_decimals = config.get("DECIMAL_PRECISION")

    value_in_range = min_val + (max_val - min_val) * score
    rounded_in_range = round(value_in_range, num_decimals)
    return int(rounded_in_range) if num_decimals == 0 else rounded_in_range
i2a = internal_to_agent

def agent_to_internal(score):
    """
    Transforms an agent-exposed score into internal
    """
    min_val = config.get("MIN_RATING")
    max_val = config.get("MAX_RATING")
    
    internal_value = (score - min_val) / (max_val - min_val)
    return internal_value
a2i= agent_to_internal

def is_within_internal_bounds(score):
    return score <= 1 and score >= 0