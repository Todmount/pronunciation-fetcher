import pathlib

def get_project_root():
    # Get the path of the script that is being executed
    current_script_path = pathlib.Path(__file__).resolve()

    for parent in current_script_path.parents:
        if (parent / 'requirements.txt').exists():
            return parent

    # If no marker is found, raise an error or handle accordingly
    raise RuntimeError("Project root could not be found.")