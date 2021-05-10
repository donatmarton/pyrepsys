#TODO: refactor handling config so 1) its easy to switch out 2) included into system at a single point 

class DefaultConfig:
    NUM_AGENTS=100
    NUM_MAX_RATERS=10

    MIN_RATING = 1
    MAX_RATING = 8

    INITIAL_REPUTATION = MAX_RATING // 2

    MEASUREMENT_ERROR = 0.5

    SIM_ROUND_MAX = 5
    SIM_ROUND_MIN = 1

    AGING_LIMIT = 2
    # 0 to only allow from current round, 1 to allow from one before too ...

