import config as CFG

def force_within_bounds(value):
    return max( min(value, CFG.MAX_RATING), CFG.MIN_RATING)