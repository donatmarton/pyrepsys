import os

from config import DefaultConfig as CFG




code_files_path = os.path.dirname( os.path.abspath(__file__) )
project_root_path = os.path.join( code_files_path, os.pardir )
simulation_artifacts_path = os.path.join( project_root_path, "simulation_artifacts" )
config_files_path = os.path.join(code_files_path, "configs")

current_sim_round = 0


def force_agent_exposed_bounds(score):
    return max( min(score, CFG.MAX_RATING), CFG.MIN_RATING)

def force_internal_bounds(score):
    return max( min(score, 1), 0)

def internal_to_agent(score):
    """
    Transforms an internal score from [0..1] to agent-exposed score
    """
    min_val = CFG.MIN_RATING
    max_val = CFG.MAX_RATING
    num_decimals = CFG.DECIMAL_PRECISION

    value_in_range = min_val + (max_val - min_val) * score
    rounded_in_range = round(value_in_range, num_decimals)
    return int(rounded_in_range) if num_decimals == 0 else rounded_in_range
i2a = internal_to_agent

def agent_to_internal(score):
    """
    Transforms an agent-exposed score into internal
    """
    min_val = CFG.MIN_RATING
    max_val = CFG.MAX_RATING
    
    internal_value = (score - min_val) / (max_val - min_val)
    return internal_value
a2i= agent_to_internal