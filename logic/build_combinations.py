import itertools
import pandas as pd

from .settings import *

def weighted_harmonic_mean(values, weights):
    if any(v <= 0 for v in values):
        return 0
    numerator = sum(weights)
    denominator = sum(w / v for w, v in zip(weights, values))
    return numerator / denominator if denominator else 0

def compute_component_weight(component_type, user_weights, relevance_matrix=RELEVANCE_MATRIX):
    total = 0
    for task, user_w in user_weights.items():
        rel = relevance_matrix[component_type].get(task, 0)
        total += user_w * rel
    return total

def generate_builds(scored_dfs, user_weights, relevance_matrix=RELEVANCE_MATRIX):
    """
    Creates all possible (GPU, CPU, RAM) builds. For each build:
      - Compute total price and power
      - Compute the final build score using a weighted harmonic mean:
         w_gpu = sum_{task}( user_weight[task] * relevance_matrix["GPU"][task] )
         w_cpu = ...
         w_ram = ...
         build_score = WeightedHarmonicMean( [gpu_score, cpu_score, ram_score], [w_gpu, w_cpu, w_ram] )
      - Compute score-to-price ratio
    Sorts the resulting builds by 'BuildScore' descending.

    Arguments:
        scored_dfs (tuple): A tuple of (scored_gpus, scored_cpus, scored_rams) in that order
    """
    gpu_records = scored_dfs[0].to_dict("records")
    cpu_records = scored_dfs[1].to_dict("records")
    ram_records = scored_dfs[2].to_dict("records")
    
    builds = []
    for gpu, cpu, ram in itertools.product(gpu_records, cpu_records, ram_records):
        # Extract names (adjust column names as needed)
        gpu_name = gpu.get("GPU") or gpu.get("Name")
        cpu_name = cpu.get("CPU") or cpu.get("Name")
        ram_name = ram.get("RAM") or ram.get("Name")
        
        # Task Score columns from your scoring step
        gpu_score = gpu.get("Task Score", 0)
        cpu_score = cpu.get("Task Score", 0)
        ram_score = ram.get("Task Score", 0)
        
        # Weighted harmonic mean requires a weight for each component
        w_gpu = compute_component_weight("GPU", user_weights, relevance_matrix)
        w_cpu = compute_component_weight("CPU", user_weights, relevance_matrix)
        w_ram = compute_component_weight("RAM", user_weights, relevance_matrix)
        
        build_score = weighted_harmonic_mean([gpu_score, cpu_score, ram_score],
                                             [w_gpu, w_cpu, w_ram])
        
        total_price = gpu["Price"] + cpu["Price"] + ram["Price"]
        total_power = gpu["Power"] + cpu["Power"] + ram["Power"]
        
        score_to_price = build_score / total_price if total_price else 0
        
        builds.append({
            "GPU": gpu_name,
            "CPU": cpu_name,
            "RAM": ram_name,
            "TotalPrice": total_price,
            "TotalPower": total_power,
            "BuildScore": build_score,
            "ScoreToPrice": score_to_price
        })
    
    builds_df = pd.DataFrame(builds)
    builds_df.sort_values("BuildScore", ascending=False, inplace=True)
    return builds_df

def filter_builds_by_price(builds_df, min_price, max_price):
    """
    Filters the final builds DataFrame by total price range.
    """
    return builds_df[
        (builds_df["TotalPrice"] >= min_price) &
        (builds_df["TotalPrice"] <= max_price)
    ]

if __name__ == "__main__":
    # Example testing:
    # Here we create dummy scored DataFrames for GPUs, CPUs, and RAMs.
    # In practice, these would be the outputs of your filtering and scoring steps.
    
    user_weights = {"Gaming": 8, "ML/AI": 5, "HPC": 3, "3D Rendering": 6}
    
    # Dummy DataFrames (assume "Task Score", "Price", "Power" columns exist)
    df_gpus = pd.DataFrame([
        {"GPU": "GPU_A", "Task Score": 90, "Price": 500, "Power": 250},
        {"GPU": "GPU_B", "Task Score": 85, "Price": 600, "Power": 300},
    ])
    df_cpus = pd.DataFrame([
        {"CPU": "CPU_A", "Task Score": 88, "Price": 200, "Power": 95},
        {"CPU": "CPU_B", "Task Score": 92, "Price": 250, "Power": 105},
    ])
    df_rams = pd.DataFrame([
        {"RAM": "RAM_A", "Task Score": 85, "Price": 100, "Power": 10},
        {"RAM": "RAM_B", "Task Score": 80, "Price": 120, "Power": 12},
    ])
    
    # Generate builds
    builds_df = generate_builds(df_gpus, df_cpus, df_rams, user_weights)
    print("All builds:\n", builds_df, "\n")
    
    # Filter by price range
    min_price = 600
    max_price = 900
    filtered_builds = filter_builds_by_price(builds_df, min_price, max_price)
    print(f"Builds in price range {min_price}-{max_price}:\n", filtered_builds)
