import pandas as pd
from .settings import PCIe_BANDWIDTH, PERFORMANCE_IMBALANCE_THRESHOLD, PENALTY_PERFORMANCE_IMBALANCE, RELEVANCE_MATRIX, USER_WEIGHTS

def weighted_harmonic_mean(values, weights):
    """
    Computes the weighted harmonic mean of a list of values.
    Returns 0 if any value is <= 0.
    """
    if any(v <= 0 for v in values):
        return 0
    numerator = sum(weights)
    denominator = sum(w / v for w, v in zip(weights, values))
    return numerator / denominator if denominator else 0

def compute_component_weight(component_type, user_weights=USER_WEIGHTS, relevance_matrix=RELEVANCE_MATRIX):
    """
    Computes the weight for a component type based on user-provided task weights and a relevance matrix.
    """
    total = 0
    for task, user_w in user_weights.items():
        rel = relevance_matrix[component_type].get(task, 0)
        total += user_w * rel
    return total

def get_first(x):
    """Helper: returns the first element if x is a list; otherwise returns x."""
    if isinstance(x, list) and len(x) > 0:
        return x[0]
    return x

def compute_build_score(row, user_weights):
    """
    Computes the final build score for a single build row.
    
    Process:
      1. Base Score: Weighted harmonic mean of GPU, CPU, and RAM scores.
      2. PCIe Version Penalty: Compares GPU's PCIe version (from its main slot) with CPU's main direct PCIe version.
      3. Performance Imbalance Penalty: If one component's score is disproportionately higher.
    
    The build DataFrame is expected to contain:
      - 'GPU Task Score', 'CPU Task Score', 'RAM Task Score'
      - 'CPU Main Direct PCIe Version' and 'GPU Main PCIe Version'
    
    Returns:
      float: The final build score.
    """
    # Retrieve individual component scores.
    gpu_score = row.get("GPU Task Score", 0)
    cpu_score = row.get("CPU Task Score", 0)
    ram_score = row.get("RAM Task Score", 0)
    
    # Compute weights.
    w_gpu = compute_component_weight("GPU", user_weights)
    w_cpu = compute_component_weight("CPU", user_weights)
    w_ram = compute_component_weight("RAM", user_weights)
    
    # Base score as weighted harmonic mean.
    base_score = weighted_harmonic_mean([gpu_score, cpu_score, ram_score], [w_gpu, w_cpu, w_ram])
    
    # PCIe penalty: compare CPU Main Direct PCIe Version vs. GPU Main PCIe Version.
    cpu_pcie = row.get("CPU Main Direct PCIe Version")
    gpu_pcie = row.get("GPU Main PCIe Version")
    if isinstance(cpu_pcie, list):
        cpu_pcie = get_first(cpu_pcie)
    if isinstance(gpu_pcie, list):
        gpu_pcie = get_first(gpu_pcie)
    if cpu_pcie is None or gpu_pcie is None:
        pcie_penalty = 1
    else:
        ratio = PCIe_BANDWIDTH.get(gpu_pcie, 1) / PCIe_BANDWIDTH.get(cpu_pcie, 1)
        # Apply penalty only if ratio is less than 1.
        pcie_penalty = min(1, ratio)
    
    # Performance imbalance penalty.
    scores = [gpu_score, cpu_score, ram_score]
    if min(scores) == 0:
        imbalance_penalty = 1
    else:
        ratio_scores = max(scores) / min(scores)
        if ratio_scores > PERFORMANCE_IMBALANCE_THRESHOLD:
            imbalance_penalty = PENALTY_PERFORMANCE_IMBALANCE
        else:
            imbalance_penalty = 1
    
    final_score = base_score * pcie_penalty * imbalance_penalty
    return final_score

def score_builds(builds_df, user_weights=USER_WEIGHTS):
    """
    Applies the build scoring function to each row in the builds DataFrame.
    Returns a new DataFrame with an added "Build Score" column.
    """
    df = builds_df.copy()
    df["Build Score"] = df.apply(lambda row: compute_build_score(row, user_weights), axis=1)
    return df

if __name__ == "__main__":
    # Example Test:
    data = [
        {
            "GPU": "GPU_A",
            "CPU": "CPU_A",
            "Motherboard": "MB_A",
            "RAM": "RAM_A",
            "GPU Task Score": 90,
            "CPU Task Score": 88,
            "RAM Task Score": 85,
            "CPU Main Direct PCIe Version": [5],
            "GPU Main PCIe Version": [4],
            "Total Power": 1000,
            "Leftover CPU Lanes": 12,
            "Price Min": 2000,
            "Price Max": 2500,
            "GPU ID": 1,
            "CPU ID": 1,
            "MB ID": 1,
            "RAM ID": 1
        },
        {
            "GPU": "GPU_B",
            "CPU": "CPU_B",
            "Motherboard": "MB_B",
            "RAM": "RAM_B",
            "GPU Task Score": 85,
            "CPU Task Score": 92,
            "RAM Task Score": 80,
            "CPU Main Direct PCIe Version": [5],
            "GPU Main PCIe Version": [4],
            "Total Power": 1050,
            "Leftover CPU Lanes": 12,
            "Price Min": 2100,
            "Price Max": 2600,
            "GPU ID": 2,
            "CPU ID": 2,
            "MB ID": 2,
            "RAM ID": 2
        }
    ]
    builds_df = pd.DataFrame(data)
    user_weights = {"Gaming": 8, "ML/AI": 10, "HPC": 3, "3D Rendering": 3}
    scored_df = score_builds(builds_df, user_weights)
    print("Scored Builds:")
    print(scored_df)
