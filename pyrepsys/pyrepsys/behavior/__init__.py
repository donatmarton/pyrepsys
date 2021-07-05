from .distort import (
    DistortDoNothingStrategy,
    DistortUpByOneAlways,
    DistortUpByOneRandom,
    DistortHugeUpRandom
)
from .rate import (
    RateRandomStrategy,
    RateLowerHalfRandom,
    RateHigherHalfRandom,
    RateNearClaimScore,
    RateFromOwnExperience,
    RateDoNothing,
    RateInvertedSlope,
    RateLinearManipulation
)