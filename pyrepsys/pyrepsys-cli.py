import argparse

import pyrepsys


def run_test(args):
    import pytest
    pytest.main(["tests/"])
    
def run_sim(args):
    if args.runparams:
        pyrepsys.run(args.runparams)
    else:
        pyrepsys.run(scenario_list=args.scenario, scenario_defaults=args.default_scenario)

def yaml_file(string: str) -> str:
    parts = string.split(".")
    if len(parts) != 2 or parts[0] == "" or parts[1] != "yaml":
        raise argparse.ArgumentTypeError("filename must be 'somefile.yaml'")
    return string


parser = argparse.ArgumentParser(
    epilog="See 'pyrepsys-cli <command> -h'"
)

subparsers = parser.add_subparsers(
    title="commands",
    description="pyrepsys can be launched in these modes:",
    required=True,
    metavar="{simulate|test}"
)

# create the parser for the "simulate" command
parser_sim = subparsers.add_parser(
    "simulate",
    aliases=["sim", "s"],
    help="Simulate selected scenarios",
    description="Simulate selected scenarios"
)
parser_sim.set_defaults(selected_mode=run_sim)
scenario_arg_group = parser_sim.add_mutually_exclusive_group(required=True)
scenario_arg_group.add_argument(
    "-rp", "--runparams",
    nargs="?",
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

# parse args
args = parser.parse_args()

# post-parsing argument processing
if args.scenario is not None and args.default_scenario is None:
    parser_sim.error("the following arguments are required with -s/--scenario: -d/--default-scenario")
if args.runparams and args.default_scenario:
    parser_sim.error("the following arguments are not allowed with -rp/--runparams: -d/--default-scenario")

# call given command
args.selected_mode(args)