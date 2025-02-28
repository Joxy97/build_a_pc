# Example usage / quick test
import matplotlib.pyplot as plt
from .data_loader import load_specifications
from .data_preprocessor import preprocess_data
from .filters import *
from .component_scoring import *
from .build_combinations import *
from .recommendation import *
from .settings import *

# 1. Load data
df_gpus, df_cpus, df_rams = load_specifications()

# 2. Preprocess data
df_gpus, df_cpus, df_rams = preprocess_data([df_gpus, df_cpus, df_rams])

# 3. Define some example filters
gpu_filters_example = {"vram_min": None, "power_max": None}
cpu_filters_example = {"cores_min": None, "power_max": None, "socket": None}
ram_filters_example = {"memory_type": None, "capacity_min": None}

# 4. Apply all filters
filtered_dfs = apply_all_filters(
    df_gpus, df_cpus, df_rams,
    gpu_filters=gpu_filters_example,
    cpu_filters=cpu_filters_example,
    ram_filters=ram_filters_example
)

# 5. Apply component scoring for a given set of task weights
user_weights = {
    "Gaming": 8,
    "ML/AI": 10,
    "HPC": 3,
    "3D Rendering": 3
}

scored_dfs = score_all_dfs(filtered_dfs, user_weights)

# 6. Create builds
builds_df = generate_builds(scored_dfs, user_weights)

# 7. Filter builds by price
min_price = 800
max_price = 840
filtered_builds = filter_builds_by_price(builds_df, min_price, max_price)

# 8. Assign recommendation scores as weighted composites (alpha=0: I want to spend least amount of money, alpha=1: I am ok with spending more if quality-to-price ratio is good)
alpha = 0.7
recommended_builds = compute_composite_recommendation_score(filtered_builds, alpha)
recommended_builds = filter_top_in_group(recommended_builds, ["GPU", "CPU"], score_col="RecommendationScore")
print(recommended_builds[["GPU", "CPU", "RAM", "TotalPower", "TotalPrice", "BuildScore", "RecommendationScore"]][:10])