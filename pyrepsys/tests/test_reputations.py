import filecmp
import os.path

import pyrepsys


# compare the repstrat with weight support but weights disabled with the no-w-support version
# reputation results should match
def test_weights_support():
    sim_dir = pyrepsys.run(
            scenario_list = [
                "weighted_AvgDiffClaimReviews_no_w.yaml",
                "weighted_AvgDiffClaimReviews_w.yaml" ],
            scenario_defaults = "test_scenario_defaults.yaml"
        )

    # access files
    file_no_w = os.path.join(sim_dir, "weighted_AvgDiffClaimReviews_no_w.csv")
    file_w = os.path.join(sim_dir, "weighted_AvgDiffClaimReviews_w.csv")

    assert filecmp.cmp(file_no_w, file_w, shallow=False) is True