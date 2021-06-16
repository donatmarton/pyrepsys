# Python Reputation System

Evaluate and compare reputation systems & their improvement methods in Python

## Installation

1. Clone the repository
2. Install dependencies

## Repository Directory Structure
```
├───thesis
├───legacy_repsys
└───pyrepsys                                # pyrepsys project dir
    ├───pyrepsys                            # source files
    ├───pyrepsys-cli.py                     # CLI for calling from terminal
    ├───run_params.yaml
    ├───scenarios                           # scenarios for simulation purposes
    │   ├───scenario_defaults.yaml
    │   ├───example_scenario_1.yaml
    │   ├───...
    ├───simulation_artifacts                # results of simulations, not cleared by pyrepsys
    │   ├───run_2021-06-15_15:12:46
    │   ├───run_2021-06-15_15:15:25
    │   ├───...
    └───tests                               # all things testing
        ├───runparams_for_tests             # testing runparams for easier calling
        ├───scenarios_for_tests             # scenarios for testing purposes
        │   ├───test_scenario_defaults.yaml
        │   ├───test_scenario_1.yaml
        │   ├───...
        ├───simulation_artifacts_from_tests # results of test simulations, cleared before tests
```

## Running

### Command Line Interface

Call pyrepsys from terminal through `pyrepsys-cli.py`. Give subcommands and a number of arguments to run a simulation or tests.

In order to use the CLI, go to the pyrepsys project directory. This is  where `pyrepsys-cli.py` is located.

```bash
cd [...]/repository/pyrepsys
```
#### Starting Simulation
Simulation is started with the `simulate` subcommand. The shorter `s` or `sim` are also available as aliases.

```bash
python3 pyrepsys-cli.py simulate [arguments]
```

There are two ways to tell pyrepsys which scenarios to simulate.

1. Use a runparams file. List all the scenarios and the defaults you need in a YAML file. Place it in the same directory as `pyrepsys-cli.py`. 

    An example runparams file named run_params.yaml could look like:
    
    ```yaml
    scenario_defaults: "my_scenario_defaults.yaml"
    scenarios:
    - "scenario.yaml"
    - "alt_scenario.yaml"
    - "third_scenario.yaml"
    ```
    
    Call a simulation with this runparams file:
    
    ```bash
    python3 pyrepsys-cli.py simulate -rp run_params.yaml
    ```
2. List scenarios and the defaults directly in the command line as arguments. E.g. to achieve the same as in the above example, type:

    ```bash
    python3 pyrepsys-cli.py simulate -s scenario.yaml alt_scenario.yaml third_scenario.yaml -d my_scenario_defaults.yaml
    ```

#### Starting Tests
To run all the tests, give the `test` or `t` subcommand.

```bash
python3 pyrepsys-cli.py test
```

TODO adding tests

### Programmatic Calling

## Reputation Methods
### Adding Reputation Methods
### Adding Improvement Methods

## Scenarios
### Adding Scenarios

## Metrics
### Adding Metrics
