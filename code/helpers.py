from config import DefaultConfig as CFG

current_sim_round = 0


def force_within_bounds(value):
    return max( min(value, CFG.MAX_RATING), CFG.MIN_RATING)