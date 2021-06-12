import os


code_files_path = os.path.dirname( os.path.abspath(__file__) )
project_root_path = os.path.join( code_files_path, os.pardir )

simulation_artifacts_path = os.path.join( project_root_path, "simulation_artifacts" )
scenarios_dir = os.path.join(project_root_path, "scenarios")
default_run_params_dir = project_root_path

tests_dir = os.path.join( project_root_path, "tests")
test_scenarios_dir = os.path.join( tests_dir, "scenarios_for_tests")