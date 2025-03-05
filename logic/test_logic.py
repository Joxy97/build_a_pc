import matplotlib.pyplot as plt
import time
from logic.data_loader import load_specifications
from logic.data_preprocessor import preprocess_data
from logic.filters import apply_all_filters, generate_all_filter_options
from logic.component_scoring import score_all_dfs
from logic.smart_picker import smart_picker
from logic.build_combinations import generate_builds, filter_builds_by_price_range
from logic.build_maker import build_maker_batched
from logic.build_scoring import score_builds
from logic.recommendation import compute_composite_recommendation_score, filter_top_in_group

def main():
    # 1. Load the data for GPUs, CPUs, Motherboards, and RAMs.
    df_gpus, df_cpus, df_mbs, df_rams = load_specifications()
    
    # 2. Preprocess the data (normalize scores, compute average price, etc.)
    df_gpus, df_cpus, df_mbs, df_rams = preprocess_data([df_gpus, df_cpus, df_mbs, df_rams])
    
    # 3. Define example filter dictionaries for each component type.
    gpu_filters_example = {
        "Brand": None,
        "Series": None,
        "Manufacturer": None,
        "Memory Capacity": (None, None),  # Minimum 8GB
        "Power": (None, None),          # Maximum 300W
        "CUDA Ready": None,             # 1 representing True
        "PCIe Version": None
    }
    
    cpu_filters_example = {
        "Brand": None,
        "Type": None,
        "Series": None,
        "Cores": (None, None),         # At least 12 cores
        "Threads": (None, None),
        "CPU Socket": None,
        "Direct PCIe Version": None,
        "Cooler": None
    }
    
    mb_filters_example = {
        "Manufacturer": None,
        "Form Factor": None,
        "CPU Socket": None,
        "Chipset": None,
        "RAM Type": None,
        "Max Capacity": (None, None),  # Supports at least 128GB
        "Modules": (None, None),
        "PCIe Version": None
    }
    
    ram_filters_example = {
        "Manufacturer": None,
        "RAM Type": None,
        "Data Rate": (None, None),  # Up to 4800
        "Capacity": (None, None),      # At least 8GB per module/kit
        "Lighting": None
    }
    
    # 4. Apply the filters.
    filtered_gpus, filtered_cpus, filtered_mbs, filtered_rams = apply_all_filters(
        df_gpus, df_cpus, df_mbs, df_rams,
        gpu_filters=gpu_filters_example,
        cpu_filters=cpu_filters_example,
        mb_filters=mb_filters_example,
        ram_filters=ram_filters_example
    )


    # 5. Compute weighted task scores.
    user_weights = {
        "Gaming": 8,
        "ML/AI": 10,
        "HPC": 3,
        "3D Rendering": 3
    }
    scored_gpus, scored_cpus, scored_mbs, scored_rams = score_all_dfs(
        (filtered_gpus, filtered_cpus, filtered_mbs, filtered_rams), user_weights
    )

    # 6. Duplicate removal for GPUs and RAMs.
    # Only GPUs and RAMs are grouped by model; CPUs and MBs remain unchanged.
    from logic.smart_picker import smart_picker
    scored_components = {
        "GPU": scored_gpus,
        "RAM": scored_rams
    }
    picked = smart_picker(scored_components)
    scored_gpus = picked["GPU"]
    scored_rams = picked["RAM"]

    '''
    # 7. Generate builds and filter them by price.
    print(scored_gpus, scored_cpus, scored_mbs, scored_rams)
    input("Build")
    builds_df = generate_builds(scored_gpus, scored_cpus, scored_mbs, scored_rams)
    input("Done")
    filtered_builds = filter_builds_by_price_range(builds_df)

    # 8. Score the builds.
    scored_df = score_builds(filtered_builds, user_weights)

    # 9. Assign recommendation scores to builds.
    recommended_builds = compute_composite_recommendation_score(scored_df)
    group_cols = ["GPU", "CPU"]
    best_builds = filter_top_in_group(recommended_builds, group_cols, score_col="Recommendation Score")
    print("\nBest Builds per (GPU, CPU) Group:")
    print(best_builds)
    '''

    # 7. Generate builds and filter them by price. Processes data in batches by CPUs, filters every batch by price, scores, calculates recommendation scores, groups by GPUs and picks top N.
    # Concatenates batches and calculates recommendation scores on the entire builds list.
    builds_df = build_maker_batched(scored_gpus, scored_cpus, scored_mbs, scored_rams, top_n=10)
    print(builds_df[["GPU", "CPU", "Motherboard", "RAM", "Total Power", "Price Min", "Build Score", "Recommendation Score"]].sort_values(by="Recommendation Score", ascending=False))

if __name__ == "__main__":
    main()
