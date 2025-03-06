import sys, os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Excel file path (update as needed)
EXCEL_PATH = resource_path(r"C:\Users\jovan\Python Projects\build_a_pc\data\Specifications.xlsx")

# Tasks used in scoring calculations
TASKS = ["Gaming", "ML/AI", "HPC", "3D Rendering"]

# Relevance matrix for component contributions (weights per task)
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

ALPHA = 0.7
MIN_PRICE = 500
MAX_PRICE = 2000

GPU_FILTERS = {
    "Brand": None,
    "Series": None,
    "Manufacturer": None,
    "Memory Capacity": (None, None),  # Minimum 8GB
    "Power": (None, None),          # Maximum 300W
    "CUDA Ready": None,             # 1 representing True
    "PCIe Version": None
}

CPU_FILTERS = {
    "Brand": None,
    "Type": None,
    "Series": None,
    "Cores": (None, None),         # At least 12 cores
    "Threads": (None, None),
    "CPU Socket": None,
    "Direct PCIe Version": None,
    "Cooler": None
}

MB_FILTERS = {
    "Manufacturer": None,
    "Form Factor": None,
    "CPU Socket": None,
    "Chipset": None,
    "RAM Type": None,
    "Max Capacity": (None, None),  # Supports at least 128GB
    "Modules": (None, None),
    "PCIe Version": None
}
   
RAM_FILTERS = {
    "Manufacturer": None,
    "RAM Type": None,
    "Data Rate": (None, None),  # Up to 4800
    "Capacity": (None, None),      # At least 8GB per module/kit
    "Lighting": None
}

USER_WEIGHTS = {
        "Gaming": 8,
        "ML/AI": 10,
        "HPC": 3,
        "3D Rendering": 3
    }

# --- New Global Parameters for Compatibility and Scoring ---

# PCIe Bandwidth mapping per generation (relative units).
# This helps to penalize PCIe generation mismatches by comparing available vs. required bandwidth.
PCIe_BANDWIDTH = {
    3: 1.0,
    4: 2.0,
    5: 4.0
}

# Base penalty factor for a PCIe generation mismatch.
# For instance, if a GPU requires PCIe 4.0 but the slot provides PCIe 3.0, the penalty factor can be:
# (PCIe_BANDWIDTH[3] / PCIe_BANDWIDTH[4]) = 1.0 / 2.0 = 0.5.
# This value can be tuned via the scoring function.
PENALTY_PCIe_GEN_MISMATCH_BASE = 1.0  # No penalty if versions match exactly

# Minimum required direct PCIe lanes from the CPU for a GPU.
# Builds where the CPU direct lanes fall short of this (e.g., < 16) should be rejected.
REQUIRED_GPU_LANES = 16

# Strict mode for checking the motherboard's main PCIe slot.
# If the primary slot does not meet the GPU's lane requirement, the build is rejected.
STRICT_MB_MAIN_SLOT = True

# Performance imbalance parameters:
# If one component's performance score is more than this factor times the other's,
# a penalty will be applied.
PERFORMANCE_IMBALANCE_THRESHOLD = 2.0  # e.g., if GPU_score > 2 x CPU_score, or vice versa
PENALTY_PERFORMANCE_IMBALANCE = 0.85   # Multiplier to the build score if imbalance is detected

# Future NVMe support:
# Set to True when implementing NVMe compatibility, to consider remaining unused CPU direct lanes.
ENABLE_NVME_CHECK = False
