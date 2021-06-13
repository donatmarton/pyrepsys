import os

import pyrepsys


def test_simulation_finishes_without_error():
    sim_dir = pyrepsys.run("test_run_params.yaml")

    assert os.path.exists( sim_dir )
    assert os.path.exists( os.path.join(sim_dir, "simulation.log") )