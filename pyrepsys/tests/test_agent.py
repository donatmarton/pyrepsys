import weakref

import pytest

import pyrepsys.agent
import pyrepsys.helpers
import pyrepsys.helper_types
import pyrepsys.errors
from pyrepsys.behavior.behavior_base import RateStrategy, DistortStrategy
import pyrepsys.config

@pytest.fixture
def mock_get(monkeypatch):
    def mock_get(config_name):
        dict = {
            "INITIAL_REPUTATION": 5,
            "MIN_RATING": 1,
            "MAX_RATING": 9,
            "DECIMAL_PRECISION": 0
        }
        return dict[config_name]
    configurator = pyrepsys.config.getConfigurator()
    monkeypatch.setattr(configurator, "get", mock_get, raising=True)
    configurator._notify_update()
    yield

@pytest.fixture
def prep_resolutions(monkeypatch):
    mock_measured_claim_steps = [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9]
    monkeypatch.setattr(pyrepsys.helpers, "measured_claim_steps", mock_measured_claim_steps, raising=True)
    mock_review_steps = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    monkeypatch.setattr(pyrepsys.helpers, "review_steps", mock_review_steps, raising=True)

@pytest.fixture
def mock_distort_strat():
    class MockDistortStrategy(DistortStrategy):
        def distort(self, distorter, measured_truth, random_seed=None):
            return measured_truth
    ds = MockDistortStrategy()
    yield ds

@pytest.fixture
def mock_rating_strat():
    class MockRateStrategy(RateStrategy):
        def rate_claim(self, rater, claim, random_seed=None):
            return claim.author_review.value
    rs = MockRateStrategy()
    yield rs

@pytest.fixture
def agent(mock_get, prep_resolutions, mock_distort_strat, mock_rating_strat):
    agent = pyrepsys.agent.Agent(
        distort_strategy=mock_distort_strat,
        rating_strategy=mock_rating_strat,
        claim_limits=pyrepsys.helper_types.ClaimLimits(min=0, max=1),
        claim_probability=1,
        rate_probability=1,
        claim_truth_assessment_inaccuracy=0.125
    )
    yield agent

@pytest.fixture
def another_agent(mock_get, prep_resolutions, mock_distort_strat, mock_rating_strat):
    agent = pyrepsys.agent.Agent(
        distort_strategy=mock_distort_strat,
        rating_strategy=mock_rating_strat,
        claim_limits=pyrepsys.helper_types.ClaimLimits(min=0, max=1),
        claim_probability=1,
        rate_probability=1,
        claim_truth_assessment_inaccuracy=0.125
    )
    yield agent

def test_author_review(agent, another_agent, rng):
    claim = agent.give_claim_opportunity(rng)
    new_author_review = pyrepsys.agent.Review(
        author=weakref.ref(agent),
        rating_score_i=0.5
    )
    non_author_review = pyrepsys.agent.Review(
        author=weakref.ref(another_agent),
        rating_score_i=0.7
    )

    assert claim is not None
    assert type(claim) is pyrepsys.agent.Claim

    assert claim.author_review is not None
    assert type(claim.author_review) is pyrepsys.agent.Review

    # try to change it in not allowed way
    with pytest.raises(AttributeError):
        claim.author_review = new_author_review
    # try to change it through designated function
    with pytest.raises(pyrepsys.errors.PermissionViolatedError):
        claim.add_author_review(agent, new_author_review)
    # try removing it
    with pytest.raises(AttributeError):
        claim.author_review = None
    with pytest.raises(pyrepsys.errors.PermissionViolatedError):
        claim.add_author_review(agent, None)
    # non-claimer agent tries to change it
    with pytest.raises(pyrepsys.errors.PermissionViolatedError):
        claim.add_author_review(another_agent, non_author_review)
    