# recommendation.py

import pandas as pd

def compute_composite_recommendation_score(builds_df, alpha=0.5):
    """
    Computes a weighted composite recommendation score for each build.
    
    The formula is:
        R = α · (P / P_max) + (1 – α) · (E / E_max)
    where:
      - P is the absolute performance score (BuildScore)
      - E is the efficiency score (ScoreToPrice)
    
    Both scores are normalized by dividing by their respective maximum values.
    
    Args:
        builds_df (pd.DataFrame): DataFrame containing builds with columns "BuildScore" and "ScoreToPrice".
        alpha (float): Trade-off parameter between 0 and 1 (from a user slider).
        
    Returns:
        pd.DataFrame: A new DataFrame sorted in descending order by "RecommendationScore".
    """
    if builds_df.empty:
        return builds_df

    P_max = builds_df["BuildScore"].max()
    E_max = builds_df["ScoreToPrice"].max()

    # Avoid division by zero by assigning zero when maximum is zero.
    if P_max == 0:
        builds_df["NormalizedPerformance"] = 0
    else:
        builds_df["NormalizedPerformance"] = builds_df["BuildScore"] / P_max

    if E_max == 0:
        builds_df["NormalizedEfficiency"] = 0
    else:
        builds_df["NormalizedEfficiency"] = builds_df["ScoreToPrice"] / E_max

    builds_df["RecommendationScore"] = (
        alpha * builds_df["NormalizedPerformance"] +
        (1 - alpha) * builds_df["NormalizedEfficiency"]
    )

    # Sort builds by the recommendation score in descending order.
    return builds_df.sort_values("RecommendationScore", ascending=False)


def filter_top_in_group(builds_df, group_cols, score_col="RecommendationScore"):
    """
    Groups the builds by the given columns (e.g., ["GPU", "CPU"]) and selects
    only the row with the highest 'score_col' in each group.
    
    Args:
        builds_df (pd.DataFrame): DataFrame of recommended builds.
        group_cols (list): List of column names to group by (e.g., ["GPU", "CPU"]).
        score_col (str): Column name of the recommendation score 
                         (e.g., "RecommendationScore", "BuildScore").
    
    Returns:
        pd.DataFrame: The top recommended builds for each group, sorted by score_col descending.
    """
    # Identify the index of the row with the max score in each group
    idx = builds_df.groupby(group_cols)[score_col].idxmax()
    
    # Select those rows
    best_df = builds_df.loc[idx].copy()
    
    # Sort the resulting subset by the recommendation score in descending order
    best_df.sort_values(score_col, ascending=False, inplace=True)
    return best_df


if __name__ == "__main__":
    # Example usage with dummy data:
    data = {
        "GPU": ["GPU_A", "GPU_B", "GPU_C"],
        "CPU": ["CPU_A", "CPU_B", "CPU_C"],
        "RAM": ["RAM_A", "RAM_B", "RAM_C"],
        "TotalPrice": [1000, 1200, 1100],
        "BuildScore": [85, 90, 80],
        "ScoreToPrice": [0.085, 0.075, 0.073]
    }
    df_builds = pd.DataFrame(data)
    
    # Suppose the user sets alpha via a slider (e.g., 0.7 means more emphasis on absolute performance)
    alpha = 0.7
    recommended_builds = compute_composite_recommendation_score(df_builds, alpha)
    print("Recommended Builds:")
    print(recommended_builds)

    data = {
        "GPU": ["RTX 4070 Super", "RTX 4070 Super", "RTX 4070 Super", "RTX 3070 Ti"],
        "CPU": ["AMD Ryzen 9 5900X", "AMD Ryzen 9 5900X", "AMD Ryzen 7 5700X", "AMD Ryzen 7 5700X"],
        "RAM": ["DDR5-6200-32/2", "DDR5-5600-32/2", "DDR4-2400-64/4", "DDR4-2400-32/2"],
        "TotalPrice": [832.0, 835.0, 847.0, 830.0],
        "BuildScore": [49.8, 49.2, 48.7, 48.3],  # Example performance scores
        "ScoreToPrice": [0.0599, 0.0589, 0.0575, 0.0582],
        "RecommendationScore": [0.9087, 0.8976, 0.8832, 0.8765]  # Example composite or other metric
    }
    builds_df = pd.DataFrame(data)
    
    print("All Recommended Builds:")
    print(builds_df)

    # Group by GPU + CPU, pick the top recommended build in each group
    best_ram_per_pair = filter_top_in_group(builds_df, ["GPU", "CPU"], score_col="RecommendationScore")
    
    print("\nBest Builds per (GPU, CPU) Group:")
    print(best_ram_per_pair)
