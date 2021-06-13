import argparse

import pyrepsys


def run_test(args):
    import pytest
    pytest.main(["tests/"])
    
def run_sim(args):
    pyrepsys.run(args.runparams)

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
    aliases=["s", "sim"],
    help="Simulate selected scenarios",
    description="Simulate selected scenarios"
    )
parser_sim.set_defaults(selected_mode=run_sim)
parser_sim.add_argument(
    "runparams",
    nargs="?",
    type=yaml_file,
    default="run_params.yaml",
    help="Name of the YAML file with the simulation run parameters"
    )

# create the parser for the "test" command
parser_test = subparsers.add_parser(
    "test",
    aliases=["t"],
    help="Run all self-tests",
    description="Run all self-tests"
    )
parser_test.set_defaults(selected_mode=run_test)

# parse args and call given command
args = parser.parse_args()
args.selected_mode(args)