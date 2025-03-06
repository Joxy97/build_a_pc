import matplotlib.pyplot as plt
import time
from logic.data_loader import load_specifications
from logic.data_preprocessor import preprocess_data
from logic.filters import apply_all_filters, generate_all_filter_options, filter_builds_by_price_range
from logic.component_scoring import score_all_dfs
from logic.smart_picker import smart_picker
from logic.build_maker import build_maker_batched
from logic.build_scoring import score_builds
from logic.recommendation import compute_composite_recommendation_score, filter_top_in_group
from .settings import *

def run_backend(alpha=ALPHA, min_price=MIN_PRICE, max_price=MAX_PRICE, gpu_filters=GPU_FILTERS, cpu_filters=CPU_FILTERS, mb_filters=MB_FILTERS, ram_filters=RAM_FILTERS, user_weights=USER_WEIGHTS):
   
    # 1. Load the data for GPUs, CPUs, Motherboards, and RAMs.
    df_gpus, df_cpus, df_mbs, df_rams = load_specifications()
    
    # 2. Preprocess the data (normalize scores, compute average price, etc.)
    df_gpus, df_cpus, df_mbs, df_rams = preprocess_data([df_gpus, df_cpus, df_mbs, df_rams])
    
    
    # 3. Apply the filters.
    filtered_gpus, filtered_cpus, filtered_mbs, filtered_rams = apply_all_filters(
        df_gpus, df_cpus, df_mbs, df_rams, gpu_filters, cpu_filters, mb_filters, ram_filters
    )

    # 4. Compute weighted task scores.
    scored_gpus, scored_cpus, scored_mbs, scored_rams = score_all_dfs(
        (filtered_gpus, filtered_cpus, filtered_mbs, filtered_rams), user_weights
    )

    # 5. Duplicate removal for GPUs and RAMs.
    # Only GPUs and RAMs are grouped by model; CPUs and MBs remain unchanged.
    scored_components = {
        "GPU": scored_gpus,
        "RAM": scored_rams
    }
    picked = smart_picker(scored_components, alpha)
    scored_gpus = picked["GPU"]
    scored_rams = picked["RAM"]

    # 6. Generate builds and filter them by price. Processes data in batches by CPUs, filters every batch by price, scores, calculates recommendation scores, groups by GPUs and picks top N.
    # Concatenates batches and calculates recommendation scores on the entire builds list.
    builds_df = build_maker_batched(scored_gpus, scored_cpus, scored_mbs, scored_rams, min_price, max_price, user_weights, alpha, top_n=10)
    builds_df = builds_df[["GPU", "CPU", "Motherboard", "RAM", "Total Power", "Price Min", "Build Score", "Recommendation Score"]].sort_values(by="Recommendation Score", ascending=False)

    return builds_df

if __name__ == "__main__":
    run_backend()
