class DefaultConfig:
    NUM_AGENTS=100
    NUM_MAX_RATERS=10

    MIN_RATING = 1
    MAX_RATING = 9
    DECIMAL_PRECISION = 0 # 0 for int

    INITIAL_REPUTATION = 5 # in user-facing range and precision

    MEASUREMENT_ERROR = 0.1 # in internal 0..1 range

    SIM_ROUND_MAX = 5
    SIM_ROUND_MIN = 1

    AGING_LIMIT = 2
    # 0 to only allow from current round, 1 to allow from one before too ...

