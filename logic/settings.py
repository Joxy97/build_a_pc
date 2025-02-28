import sys, os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Usage:
EXCEL_PATH = resource_path("data/Specifications.xlsx")


TASKS = ["Gaming", "ML/AI", "HPC", "3D Rendering"]

RELEVANCE_MATRIX = {
    "GPU": {
        "Gaming": 0.5,
        "ML/AI": 0.4,
        "HPC": 0.2,
        "3D Rendering": 0.4
    },
    "CPU": {
        "Gaming": 0.3,
        "ML/AI": 0.3,
        "HPC": 0.5,
        "3D Rendering": 0.3
    },
    "RAM": {
        "Gaming": 0.2,
        "ML/AI": 0.3,
        "HPC": 0.3,
        "3D Rendering": 0.3
    }
}