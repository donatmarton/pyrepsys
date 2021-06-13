import os


code_files_path = os.path.dirname( os.path.abspath(__file__) )
project_root_path = os.path.join( code_files_path, os.pardir )

simulation_artifacts_path = os.path.join( project_root_path, "simulation_artifacts" )
scenarios_dir = os.path.join(project_root_path, "scenarios")
run_params_dir = project_root_path