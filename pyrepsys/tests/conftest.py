import os
import shutil
import pytest

import pyrepsys


@pytest.fixture(scope="session")
def paths():
    dict = {}
    dict["TESTS_DIR"] = os.path.dirname( os.path.abspath(__file__) )
    dict["TEST_SCENARIOS_DIR"] = os.path.join( dict["TESTS_DIR"], "scenarios_for_tests")
    dict["TEST_SIMULATION_ARTIFACTS_DIR"] = os.path.join( dict["TESTS_DIR"], "simulation_artifacts_from_tests" )
    dict["TEST_RUN_PARAMS_DIR"] = os.path.join( dict["TESTS_DIR"], "runparams_for_tests")
    return dict

@pytest.fixture(autouse=True, scope="session")
def prepare_pyrepsys_paths_for_tests(paths):
    pyrepsys.set_scenarios_dir(paths["TEST_SCENARIOS_DIR"])
    pyrepsys.set_run_params_dir(paths["TEST_RUN_PARAMS_DIR"])
    pyrepsys.set_simulation_artifacts_dir(paths["TEST_SIMULATION_ARTIFACTS_DIR"])
    # clean the artifacts dir of past runs:
    try: shutil.rmtree(paths["TEST_SIMULATION_ARTIFACTS_DIR"])
    except: FileNotFoundError