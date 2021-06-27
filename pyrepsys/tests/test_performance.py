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

def test_profile_short(tmp_profiling_file, results_file):
    cProfile.run(
        'pyrepsys.run(scenario_list=["perf_base.yaml"], scenario_defaults="perf_base.yaml")',
        tmp_profiling_file)    

    p = pstats.Stats(tmp_profiling_file, stream=results_file)

    results_file.write("===========================================================================\n")
    results_file.write("PROFILE: Short run (perf_base.yaml)\n")
    results_file.write("===========================================================================\n\n")
    p.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(20)
    p.strip_dirs().sort_stats(SortKey.TIME).print_stats(20)

def test_profile_short_noage(tmp_profiling_file, results_file):
    cProfile.run(
        'pyrepsys.run(scenario_list=["perf_noage.yaml"], scenario_defaults="perf_base.yaml")',
        tmp_profiling_file)    

    p = pstats.Stats(tmp_profiling_file, stream=results_file)

    results_file.write("===========================================================================\n")
    results_file.write("PROFILE: Short run, no aging (perf_noage.yaml)\n")
    results_file.write("===========================================================================\n\n")
    p.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(20)
    p.strip_dirs().sort_stats(SortKey.TIME).print_stats(20)

def test_profile_long(tmp_profiling_file, results_file):
    cProfile.run(
        'pyrepsys.run(scenario_list=["perf_long.yaml"], scenario_defaults="perf_base.yaml")',
        tmp_profiling_file)    

    p = pstats.Stats(tmp_profiling_file, stream=results_file)

    results_file.write("===========================================================================\n")
    results_file.write("PROFILE: Long run (perf_long.yaml)\n")
    results_file.write("===========================================================================\n\n")
    p.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(20)
    p.strip_dirs().sort_stats(SortKey.TIME).print_stats(20)

def test_benchmark_short(results_file):
    timer = timeit.Timer(
        'pyrepsys.run(scenario_list=["perf_base.yaml"], scenario_defaults="perf_base.yaml")',
        'gc.enable(); import pyrepsys'
    )

    results = timer.repeat(repeat=3, number=1)

    results_file.write("===========================================================================\n")
    results_file.write("BENCHMARK: Short run (perf_base.yaml)\n")
    results_file.write("===========================================================================\n\n")
    
    results_file.write("Runtimes:\n")
    for res in results:
        d = timedelta(seconds=res)
        results_file.write("{}\n".format(str(d)))