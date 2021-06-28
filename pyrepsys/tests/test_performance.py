import os.path 
import cProfile
import pstats
from pstats import SortKey
import timeit
from datetime import timedelta

import pytest

import pyrepsys


@pytest.fixture()
def results_file(paths):
    results_file_path = os.path.join(paths["TEST_SIMULATION_ARTIFACTS_DIR"], "performance")
    if not os.path.exists(results_file_path):
        write_warning = True
    else: write_warning = False
    with open(results_file_path, 'a') as results_file:
        if write_warning:
            results_file.write("! The profiler modules are designed to provide an execution profile for a given program, not for benchmarking purposes.\n")
            results_file.write("! Runtimes below include overhead from extensive profiling.\n\n")
        yield results_file

@pytest.fixture()
def tmp_profiling_file(tmpdir):
    file = os.path.join(tmpdir, "profiling_test_run")
    yield file

@pytest.mark.perf
@pytest.mark.parametrize(
    "scenario, desc",
    [("perf_base.yaml", "short run"), 
    pytest.param("perf_noage.yaml", "short run, no aging", marks=pytest.mark.long), 
    pytest.param("perf_long.yaml", "long run", marks=pytest.mark.long)
    ])
def test_do_profiling(tmp_profiling_file, results_file, scenario, desc):
    statement = 'pyrepsys.run(scenario_list=["{}"], scenario_defaults="perf_base.yaml")'.format(scenario)
    cProfile.run(statement, tmp_profiling_file)    

    p = pstats.Stats(tmp_profiling_file, stream=results_file)

    results_file.write("\n===========================================================================\n")
    results_file.write("PROFILE: {} ({})\n".format(desc, scenario))
    results_file.write("===========================================================================\n\n")
    p.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(20)
    p.strip_dirs().sort_stats(SortKey.TIME).print_stats(20)

@pytest.mark.perf
@pytest.mark.parametrize(
    "scenario, desc",
    [("perf_base.yaml", "short run"), 
    pytest.param("perf_long.yaml", "long run", marks=pytest.mark.long)
    ])
def test_do_benchmark(results_file, scenario, desc):
    statement = 'pyrepsys.run(scenario_list=["{}"], scenario_defaults="perf_base.yaml")'.format(scenario)
    timer = timeit.Timer(
        statement,
        'gc.enable(); import pyrepsys'
    )

    results = timer.repeat(repeat=3, number=1)

    results_file.write("\n===========================================================================\n")
    results_file.write("BENCHMARK: {} ({})\n".format(desc, scenario))
    results_file.write("===========================================================================\n\n")
    
    results_file.write("Runtimes:\n")
    for res in results:
        d = timedelta(seconds=res)
        results_file.write("{:8.2f}s ({})\n".format(res, str(d)))
    results_file.write("\n")