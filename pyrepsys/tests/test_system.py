import os

import pytest

import pyrepsys


def test_simulation_finishes_without_error():
    sim_dir = pyrepsys.run(run_params_file_name="run_short_scenario.yaml")

def test_no_improvements_given():
    sim_dir = pyrepsys.run(
        scenario_list=["short_scenario_no_improvements.yaml"], 
        scenario_defaults="test_scenario_defaults.yaml"
    )

def test_incorrect_run_calls():
    with pytest.raises(TypeError):
        # neither runparams nor scenario list
        pyrepsys.run()
    with pytest.raises(TypeError):
        # both runparams and scenario list
        pyrepsys.run(
            run_params_file_name="run_short_scenario.yaml",
            scenario_list=["short_scenario_no_improvements.yaml"]
        )
    with pytest.raises(TypeError):
        # no default given
        pyrepsys.run(scenario_list=["short_scenario_no_improvements.yaml"])
    with pytest.raises(TypeError):
        # scenario list not as list
        pyrepsys.run(
            scenario_list="short_scenario_no_improvements.yaml",
            scenario_defaults="test_scenario_defaults.yaml"
        )
def test_three_successive_runs():
    run1_sim_dir = pyrepsys.run(run_params_file_name="run_short_scenario.yaml")
    run2_sim_dir = pyrepsys.run(run_params_file_name="run_short_scenario.yaml")
    run3_sim_dir = pyrepsys.run("run_short_scenario.yaml")

    assert os.path.exists( run1_sim_dir )
    assert os.path.exists( run2_sim_dir )
    assert os.path.exists( run3_sim_dir )
    assert run1_sim_dir != run2_sim_dir
    assert run1_sim_dir != run3_sim_dir
    assert run2_sim_dir != run3_sim_dir

def test_artifact_dir_and_logfile_generation():
    sim_dir = pyrepsys.run("run_short_scenario.yaml")

    assert os.path.exists( sim_dir )
    assert os.path.exists( os.path.join(sim_dir, "simulation.log") )

def test_scenarios_manual_evaluation():
    pyrepsys.run("for_manual_evaluation.yaml")
    assert True