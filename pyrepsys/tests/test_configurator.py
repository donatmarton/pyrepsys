import pytest

import pyrepsys.config
import pyrepsys.helpers
import pyrepsys.scenario_simulator
import pyrepsys.instantiator
import pyrepsys.errors


@pytest.fixture
def configurator(paths):
    configurator = pyrepsys.config.getConfigurator()
    configurator.scenarios_dir = paths["TEST_SCENARIOS_DIR"]
    configurator.instantiator = pyrepsys.instantiator.Instantiator()
    yield configurator

@pytest.fixture
def simulator():
    return pyrepsys.scenario_simulator.ScenarioSimulator()

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

    pyrepsys.helpers._configure_system_resolutions()

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

    pyrepsys.helpers._configure_system_resolutions()

    expected_steps = [0, 1]
    assert pyrepsys.helpers.review_steps == expected_steps
    assert pyrepsys.helpers.measured_claim_steps == expected_steps

def test_small_resolution(monkeypatch, configurator):
    monkeypatch.setitem(configurator._active_config, "MIN_RATING", 1)
    monkeypatch.setitem(configurator._active_config, "MAX_RATING", 9)
    monkeypatch.setitem(configurator._active_config, "MEASURED_CLAIM_RESOLUTION", 0.01)
    monkeypatch.setitem(configurator._active_config, "REVIEW_RESOLUTION", 1)

    pyrepsys.helpers._configure_system_resolutions()

    expected_review_steps = [x for x in range(1,10)]
    assert pyrepsys.helpers.review_steps == expected_review_steps

    expected_measured_claim_steps = [1+ 0.01*x for x in range(int(1+ 8/0.01))]
    # [1, 1.5, 2, ... 8, 8.5, 9]
    assert pyrepsys.helpers.measured_claim_steps == expected_measured_claim_steps

def test_incorrect_configuration(monkeypatch, configurator):
    # min = max
    monkeypatch.setitem(configurator._active_config, "MIN_RATING", 1)
    monkeypatch.setitem(configurator._active_config, "MAX_RATING", 1)
    monkeypatch.setitem(configurator._active_config, "MEASURED_CLAIM_RESOLUTION", 1)
    monkeypatch.setitem(configurator._active_config, "REVIEW_RESOLUTION", 1)
    with pytest.raises(pyrepsys.helpers.ConfigurationError):
        pyrepsys.helpers._configure_system_resolutions()

    # min > max
    monkeypatch.setitem(configurator._active_config, "MIN_RATING", 5)
    monkeypatch.setitem(configurator._active_config, "MAX_RATING", 3)
    with pytest.raises(pyrepsys.helpers.ConfigurationError):
        pyrepsys.helpers._configure_system_resolutions()

    # step larger than span
    monkeypatch.setitem(configurator._active_config, "MIN_RATING", 1)
    monkeypatch.setitem(configurator._active_config, "MAX_RATING", 5)
    monkeypatch.setitem(configurator._active_config, "MEASURED_CLAIM_RESOLUTION", 6)
    monkeypatch.setitem(configurator._active_config, "REVIEW_RESOLUTION", 5)
    with pytest.raises(pyrepsys.helpers.ConfigurationError):
        pyrepsys.helpers._configure_system_resolutions()

    # step doesnt fit in span without remainder
    monkeypatch.setitem(configurator._active_config, "MIN_RATING", 1)
    monkeypatch.setitem(configurator._active_config, "MAX_RATING", 5)
    monkeypatch.setitem(configurator._active_config, "MEASURED_CLAIM_RESOLUTION", 3)
    monkeypatch.setitem(configurator._active_config, "REVIEW_RESOLUTION", 3)
    with pytest.raises(pyrepsys.helpers.ConfigurationError):
        pyrepsys.helpers._configure_system_resolutions()

def test_config_items_extended_with_settings(configurator, simulator):
    configurator.read_default_configuration("test_scenario_defaults.yaml")
    configurator.read_configuration("test_config_items_extended_settings.yaml")

    configurator.configure_system(simulator)

    assert simulator._reputation_strategy.local_config is not None
    assert simulator._reputation_strategy.get_local_config("repstrat_test_param") == 23
    with pytest.raises(pyrepsys.errors.ConfigurationError):
        simulator._reputation_strategy.get_local_config("param_not_in_config")
    
    assert simulator._improvement_handler.local_config is not None
    assert simulator._improvement_handler.get_local_config("limit") == 2
    assert simulator._improvement_handler._next_handler.local_config is None
    with pytest.raises(pyrepsys.errors.ConfigurationError):
        simulator._improvement_handler._next_handler.get_local_config("any_param")
    
    assert simulator.agents[0].distort_strategy.local_config is not None
    assert simulator.agents[0].distort_strategy.get_local_config("ds_test_param") is False
    with pytest.raises(pyrepsys.errors.ConfigurationError):
        assert simulator.agents[0].distort_strategy.get_local_config("ds_test_param2")
    assert simulator.agents[0].rating_strategy.local_config is None
    with pytest.raises(pyrepsys.errors.ConfigurationError):
        simulator.agents[0].rating_strategy.get_local_config("any_param")
    
    assert simulator.agents[1].distort_strategy.local_config is not None
    assert simulator.agents[1].distort_strategy.get_local_config("ds_test_param") is True
    assert simulator.agents[1].distort_strategy.get_local_config("ds_test_param2") == 12
    assert simulator.agents[1].rating_strategy.local_config is not None
    assert simulator.agents[1].rating_strategy.get_local_config("rs_test_param") is False