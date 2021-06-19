

import pytest

import pyrepsys.config
import pyrepsys.helpers


@pytest.fixture
def configurator():
    return pyrepsys.config.Configurator()

@pytest.fixture(autouse=True)
def resolution_steps():
    yield
    pyrepsys.helpers.review_steps = None
    pyrepsys.helpers.measured_claim_steps = None

def test_correct_resolutions(monkeypatch, configurator):
    monkeypatch.setitem(configurator._active_config, "MIN_RATING", 1)
    monkeypatch.setitem(configurator._active_config, "MAX_RATING", 9)
    monkeypatch.setitem(configurator._active_config, "MEASURED_CLAIM_RESOLUTION", 0.5)
    monkeypatch.setitem(configurator._active_config, "REVIEW_RESOLUTION", 1)

    configurator._configure_system_resolutions()

    expected_review_steps = [x for x in range(1,10)]
    assert pyrepsys.helpers.review_steps == expected_review_steps

    expected_measured_claim_steps = [1+ 0.5*x for x in range(int(1+ 8/0.5))]
    # [1, 1.5, 2, ... 8, 8.5, 9]
    assert pyrepsys.helpers.measured_claim_steps == expected_measured_claim_steps

def test_binary_resolutions(monkeypatch, configurator):
    monkeypatch.setitem(configurator._active_config, "MIN_RATING", 0)
    monkeypatch.setitem(configurator._active_config, "MAX_RATING", 1)
    monkeypatch.setitem(configurator._active_config, "MEASURED_CLAIM_RESOLUTION", 1)
    monkeypatch.setitem(configurator._active_config, "REVIEW_RESOLUTION", 1)

    configurator._configure_system_resolutions()

    expected_steps = [0, 1]
    assert pyrepsys.helpers.review_steps == expected_steps
    assert pyrepsys.helpers.measured_claim_steps == expected_steps

def test_incorrect_configuration(monkeypatch, configurator):
    # min = max
    monkeypatch.setitem(configurator._active_config, "MIN_RATING", 1)
    monkeypatch.setitem(configurator._active_config, "MAX_RATING", 1)
    monkeypatch.setitem(configurator._active_config, "MEASURED_CLAIM_RESOLUTION", 1)
    monkeypatch.setitem(configurator._active_config, "REVIEW_RESOLUTION", 1)
    with pytest.raises(pyrepsys.helpers.ConfigurationError):
        configurator._configure_system_resolutions()

    # min > max
    monkeypatch.setitem(configurator._active_config, "MIN_RATING", 5)
    monkeypatch.setitem(configurator._active_config, "MAX_RATING", 3)
    with pytest.raises(pyrepsys.helpers.ConfigurationError):
        configurator._configure_system_resolutions()

    # step larger than span
    monkeypatch.setitem(configurator._active_config, "MIN_RATING", 1)
    monkeypatch.setitem(configurator._active_config, "MAX_RATING", 5)
    monkeypatch.setitem(configurator._active_config, "MEASURED_CLAIM_RESOLUTION", 6)
    monkeypatch.setitem(configurator._active_config, "REVIEW_RESOLUTION", 5)
    with pytest.raises(pyrepsys.helpers.ConfigurationError):
        configurator._configure_system_resolutions()

    # step doesnt fit in span without remainder
    monkeypatch.setitem(configurator._active_config, "MIN_RATING", 1)
    monkeypatch.setitem(configurator._active_config, "MAX_RATING", 5)
    monkeypatch.setitem(configurator._active_config, "MEASURED_CLAIM_RESOLUTION", 3)
    monkeypatch.setitem(configurator._active_config, "REVIEW_RESOLUTION", 3)
    with pytest.raises(pyrepsys.helpers.ConfigurationError):
        configurator._configure_system_resolutions()