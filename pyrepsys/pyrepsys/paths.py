import os


code_files_path = os.path.dirname( os.path.abspath(__file__) )
project_root_path = os.path.join( code_files_path, os.pardir )
simulation_artifacts_path = os.path.join( project_root_path, "simulation_artifacts" )
config_files_path = os.path.join(code_files_path, "configs")
default_run_params_dir = project_root_path