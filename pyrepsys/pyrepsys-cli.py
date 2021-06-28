import argparse

import pyrepsys


def run_test(args):
    import pytest
    pytest_args = ["tests/"]
    if args.verbose: pytest_args.append("-v")
    if args.markexpr: 
        pytest_args.append("-m")
        pytest_args.append(args.markexpr)
    pytest.main(pytest_args)
    
def run_sim(args):
    if args.runparams:
        pyrepsys.run(args.runparams)
    else:
        pyrepsys.run(scenario_list=args.scenario, scenario_defaults=args.default_scenario)

def run_scenario_creator(args):
    pyrepsys.run_scenario_creator(
        generator=args.generator, 
        runparams_file_name=args.runparams,
        scenario_defaults=args.default_scenario,
        clean=args.clean
    )

def yaml_file(string: str) -> str:
    parts = string.split(".")
    if len(parts) != 2 or parts[0] == "" or parts[1] != "yaml":
        raise argparse.ArgumentTypeError("filename must be 'somefile.yaml'")
    return string


parser = argparse.ArgumentParser(
    epilog="See 'pyrepsys-cli <command> -h'"
)
parser.set_defaults(selected_mode=None)

subparsers = parser.add_subparsers(
    title="commands",
    description="pyrepsys can be launched in these modes:",
    metavar="{simulate|test|scenario-creator}"
)

# create the parser for the "simulate" command
parser_sim = subparsers.add_parser(
    "simulate",
    aliases=["sim", "s"],
    help="Simulate selected scenarios",
    description="Simulate selected scenarios",
    usage="%(prog)s -rp RUNPARAMS\n   or: %(prog)s -s SCENARIO [SCENARIO ...] -d DEFAULT_SCENARIO"
)
parser_sim.set_defaults(selected_mode=run_sim)
scenario_arg_group = parser_sim.add_mutually_exclusive_group(required=True)
scenario_arg_group.add_argument(
    "-rp", "--runparams",
    type=yaml_file,
    help="Name of the YAML file with the simulation run parameters"
)
scenario_arg_group.add_argument(
    "-s", "--scenario",
    nargs="*",
    type=yaml_file,
    help="Name of the YAML file(s) with scenarios to simulate"
)
parser_sim.add_argument(
    "-d", "--default-scenario",
    type=yaml_file,
    help="Name of the YAML file with the default scenario settings. Required if scenarios are given as arguments"
)

# create the parser for the "test" command
parser_test = subparsers.add_parser(
    "test",
    aliases=["t"],
    help="Run all self-tests",
    description="Run all self-tests"
    )
parser_test.set_defaults(selected_mode=run_test)
parser_test.add_argument(
    "-v", "--verbose",
    action="store_true",
    help="Increase verbosity of pytest output"
)
parser_test.add_argument(
    "-m", "--markexpr",
    help="Only run tests matching the given mark expression"
)

# create the parser for the "scenario-creator" command
parser_sc = subparsers.add_parser(
    "scenario-creator",
    aliases=["sc"],
    help="Generate scenarios from a template",
    description="Generate scenarios from a template. Create a runparams file with the generated scenarios."
    )
parser_sc.set_defaults(selected_mode=run_scenario_creator)
parser_sc.add_argument(
    "-c", "--clean",
    action="store_true",
    help="Clear all scenarios previously generated by the scenario creator"
)
parser_sc.add_argument(
    "-g", "--generator",
    type=yaml_file,
    help="Name of the YAML file with the parameter variants"
)
parser_sc.add_argument(
    "-rp", "--runparams",
    type=yaml_file,
    help="Name of the YAML file where to write run parameters based on scenarios created. Optional"
)
parser_sc.add_argument(
    "-d", "--default-scenario",
    type=yaml_file,
    help="Name of the YAML file with the default scenario settings. Optional. Written to run params file if given"
)

# parse args
args = parser.parse_args()

if not args.selected_mode:
    parser.error("one of the subcommands is required: {simulate|test|scenario-creator}")

# post-parsing argument processing
if args.selected_mode == run_sim:
    if args.scenario is not None and args.default_scenario is None:
        parser_sim.error("the following arguments are required with -s/--scenario: -d/--default-scenario")
    if args.runparams and args.default_scenario:
        parser_sim.error("the following arguments are not allowed with -rp/--runparams: -d/--default-scenario")
if args.selected_mode == run_scenario_creator:
    if args.generator is None and args.clean is False:
        parser_sc.error("one of the arguments -g/--generator -c/--clean is required")

# call given command
args.selected_mode(args)