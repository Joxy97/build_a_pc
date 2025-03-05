import pandas as pd
from .settings import ALPHA

def pick_best_by_model(df, alpha=ALPHA):
    """
    For a scored GPU or RAM DataFrame (which must include at least the following columns:
      - "Model" (as string),
      - "Task Score" (the normalized performance score for that component),
      - "Price Min"
    ),
    this function computes an efficiency metric for each row:
          ScoreToPrice = Task Score / Price Min,
    then within each Model group, it normalizes both Task Score and ScoreToPrice by the group's maximum,
    computes a composite recommendation score as:
          R = α * (Task Score / P_max) + (1 - α) * (ScoreToPrice / E_max),
    and selects the row with the highest recommendation score for that model.
    
    Args:
        df (pd.DataFrame): Scored DataFrame for a component (GPU or RAM).
        alpha (float): Weighting factor (between 0 and 1) from settings.
    
    Returns:
        pd.DataFrame: A new DataFrame containing one row per unique model (the best variant).
    """
    # Ensure that "Model" is treated as string
    df = df.copy()
    df["Model"] = df["Model"].astype(str)
    
    # Compute efficiency: ScoreToPrice = Task Score / Price Min (if Price Min > 0)
    df["ScoreToPrice"] = df.apply(lambda row: row["Task Score"] / row["Price Min"] if row["Price Min"] > 0 else 0, axis=1)
    
    best_rows = []
    # Group by "Model"
    groups = df.groupby("Model")
    for model, group in groups:
        group = group.copy()
        P_max = group["Task Score"].max()
        E_max = group["ScoreToPrice"].max()
        # Normalize within the group (if maximums are nonzero)
        group["NormalizedPerformance"] = group["Task Score"] / P_max if P_max != 0 else 0
        group["NormalizedEfficiency"] = group["ScoreToPrice"] / E_max if E_max != 0 else 0
        # Compute composite score
        group["RecommendationScore"] = alpha * group["NormalizedPerformance"] + (1 - alpha) * group["NormalizedEfficiency"]
        # Select the best row in the group
        best_row = group.loc[group["RecommendationScore"].idxmax()]
        best_rows.append(best_row)
    result = pd.DataFrame(best_rows)
    # Drop temporary columns
    for col in ["NormalizedPerformance", "NormalizedEfficiency", "RecommendationScore", "ScoreToPrice"]:
        if col in result.columns:
            result.drop(columns=[col], inplace=True)
    return result

def smart_picker(scored_components):
    """
    Given a dictionary mapping component categories (e.g., "GPU" and "RAM")
    to their scored DataFrames, group each DataFrame by the "Model" column and select the best variant.
    
    Only components that have a "Model" column are processed; others are returned as-is.
    
    Args:
        scored_components (dict): For example, {"GPU": df_gpu, "RAM": df_ram}
    
    Returns:
        dict: A dictionary with the same keys, each mapping to a filtered DataFrame with one row per unique model.
    """
    picked = {}
    for comp, df in scored_components.items():
        if "Model" in df.columns:
            picked[comp] = pick_best_by_model(df)
        else:
            picked[comp] = df.copy()
    return picked

if __name__ == "__main__":
    # Example test with dummy data for GPUs
    gpu_data = [
        {"Model": "RTX 3060", "Task Score": 90, "Price Min": 400, "OtherSpec": "Variant A"},
        {"Model": "RTX 3060", "Task Score": 85, "Price Min": 380, "OtherSpec": "Variant B"},
        {"Model": "RTX 3070", "Task Score": 92, "Price Min": 500, "OtherSpec": "Variant C"},
        {"Model": "RTX 3070", "Task Score": 88, "Price Min": 480, "OtherSpec": "Variant D"}
    ]
    df_gpu = pd.DataFrame(gpu_data)
    
    best_gpu = pick_best_by_model(df_gpu, alpha=ALPHA)
    print("Best GPU variants by model:")
    print(best_gpu)
    
    # Example test with dummy data for RAMs
    ram_data = [
        {"Model": "HyperX Fury", "Task Score": 85, "Price Min": 100, "OtherSpec": "Variant A"},
        {"Model": "HyperX Fury", "Task Score": 82, "Price Min": 95, "OtherSpec": "Variant B"},
        {"Model": "Corsair Vengeance", "Task Score": 88, "Price Min": 120, "OtherSpec": "Variant C"},
        {"Model": "Corsair Vengeance", "Task Score": 90, "Price Min": 130, "OtherSpec": "Variant D"}
    ]
    df_ram = pd.DataFrame(ram_data)
    
    best_ram = pick_best_by_model(df_ram, alpha=ALPHA)
    print("\nBest RAM variants by model:")
    print(best_ram)
    
    # Example dictionary for smart_picker:
    scored_components = {
        "GPU": df_gpu,
        "RAM": df_ram
    }
    picked = smart_picker(scored_components)
    for comp, df in picked.items():
        print(f"\nBest {comp} variants by model:")
        print(df)
