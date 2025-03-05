import pandas as pd
from .settings import ALPHA  # Default alpha value, e.g., 0.7, to be tuned via GUI later

def compute_composite_recommendation_score(builds_df, alpha=ALPHA):
    """
    Computes a weighted composite recommendation score for each build.
    
    This version uses:
      - P: Absolute performance score ("Build Score")
      - E: Efficiency score computed as Build Score divided by Price Min.
    
    Both scores are normalized (by dividing by their maximum values) and then balanced:
        R = α * (P / P_max) + (1 – α) * (E / E_max)
    
    Args:
        builds_df (pd.DataFrame): DataFrame containing builds with columns "Build Score" and "Price Min".
        alpha (float): Trade-off parameter between 0 and 1. α=1 for pure performance, α=0 for pure efficiency.
        
    Returns:
        pd.DataFrame: A new DataFrame sorted in descending order by "Recommendation Score".
    """
    if builds_df.empty:
        return builds_df

    builds_df = builds_df.copy()
    # Calculate efficiency as Build Score divided by Price Min.
    builds_df["Score To Price"] = builds_df.apply(
        lambda row: row["Build Score"] / row["Price Min"] if row["Price Min"] > 0 else 0, axis=1
    )

    # Normalize performance and efficiency scores.
    P_max = builds_df["Build Score"].max()
    E_max = builds_df["Score To Price"].max()

    builds_df["Normalized Performance"] = builds_df["Build Score"] / P_max if P_max != 0 else 0
    builds_df["Normalized Efficiency"] = builds_df["Score To Price"] / E_max if E_max != 0 else 0

    builds_df["Recommendation Score"] = (
        alpha * builds_df["Normalized Performance"] +
        (1 - alpha) * builds_df["Normalized Efficiency"]
    ) * 100

    return builds_df.sort_values("Recommendation Score", ascending=False)


def filter_top_in_group(builds_df, group_cols, score_col="Recommendation Score"):
    """
    Groups the builds by the given columns (e.g., ["GPU", "CPU"]) and selects
    only the row with the highest 'score_col' in each group.
    
    Args:
        builds_df (pd.DataFrame): DataFrame of recommended builds.
        group_cols (list): List of column names to group by (e.g., ["GPU", "CPU"]).
        score_col (str): Column name of the recommendation score.
    
    Returns:
        pd.DataFrame: The top recommended builds for each group, sorted by score_col descending.
    """
    idx = builds_df.groupby(group_cols)[score_col].idxmax()
    best_df = builds_df.loc[idx].copy()
    best_df.sort_values(score_col, ascending=False, inplace=True)
    return best_df


if __name__ == "__main__":
    # Example usage with dummy data.
    data = {
        "GPU": ["GPU_A", "GPU_B", "GPU_C"],
        "CPU": ["CPU_A", "CPU_B", "CPU_C"],
        "Motherboard": ["MB_A", "MB_B", "MB_C"],
        "RAM": ["RAM_A", "RAM_B", "RAM_C"],
        "Price Min": [1000, 1200, 1100],
        "Build Score": [85, 90, 80]
    }
    df_builds = pd.DataFrame(data)
    
    # Use default ALPHA from settings or override (e.g., 0.7 emphasizes performance).
    recommended_builds = compute_composite_recommendation_score(df_builds, alpha=ALPHA)
    print("Recommended Builds:")
    print(recommended_builds)
    
    # Example grouping: Group by GPU and CPU, then select the best build per group.
    group_cols = ["GPU", "CPU"]
    best_builds = filter_top_in_group(recommended_builds, group_cols, score_col="Recommendation Score")
    print("\nBest Builds per (GPU, CPU) Group:")
    print(best_builds)

