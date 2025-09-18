from common.path_utils import get_project_root

try:
    PROJECT_ROOT = get_project_root()
except RuntimeError:
    raise