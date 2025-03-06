import pandas as pd
from .settings import *

def compute_component_score(row, user_weights, score_columns=None):
    """
    Calculates the weighted average score for a single component (row) based on user weights.
    
    Args:
        row (pd.Series): A row from the DataFrame representing one component.
        user_weights (dict): Dictionary with keys as task names (e.g., "Gaming", "ML/AI", "HPC", "3D Rendering")
                             and values as the corresponding user-provided weight.
        score_columns (dict, optional): Mapping of task names to DataFrame column names.
            Defaults to:
            {
                "Gaming": "Gaming Score",
                "ML/AI": "ML/AI Score",
                "HPC": "HPC Score",
                "3D Rendering": "3D Rendering Score"
            }
    
    Returns:
        float: The computed weighted score.
    """
    if score_columns is None:
        score_columns = {
            "Gaming": "Gaming Score",
            "ML/AI": "ML/AI Score",
            "HPC": "HPC Score",
            "3D Rendering": "3D Rendering Score"
        }
        
    numerator = 0
    denominator = 0
    for task, weight in user_weights.items():
        col_name = score_columns.get(task, task + " Score")
        if col_name in row:
            numerator += weight * row[col_name]
            denominator += weight
    return numerator / denominator if denominator else 0

def compute_component_scores_for_df(df, user_weights):
    """
    Applies the weighted score calculation to every row in the DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame containing component data with score columns.
        user_weights (dict): Dictionary with task names and user-provided weights.
    
    Returns:
        pd.DataFrame: A new DataFrame with an added column "Task Score".
    """
    df = df.copy()
    df["Task Score"] = df.apply(
        lambda row: compute_component_score(row, user_weights),
        axis=1
    )
    return df

def score_all_dfs(filtered_dfs, user_weights):
    """
    Applies the weighted score calculation for all DataFrames in the tuple.
    
    Since motherboards do not have performance score columns, they are passed through unchanged.
    
    Args:
        filtered_dfs (tuple): A tuple of DataFrames, expected order: (GPUs, CPUs, Motherboards, RAMs).
        user_weights (dict): Dictionary with task names and user-provided weights.
    
    Returns:
        tuple: A tuple of DataFrames where GPUs, CPUs, and RAMs have an added "Task Score" column,
               and Motherboards are unchanged.
    """
    scored_dfs = []
    for df in filtered_dfs:
        # Only score DataFrames that have performance score columns
        if "Gaming Score" in df.columns:
            scored_dfs.append(compute_component_scores_for_df(df, user_weights))
        else:
            scored_dfs.append(df)
    return tuple(scored_dfs)

if __name__ == "__main__":
    # Example usage: Test on a small DataFrame
    test_data = {
        "Gaming Score": [80, 90],
        "ML/AI Score": [70, 95],
        "HPC Score": [75, 85],
        "3D Rendering Score": [90, 80]
    }
    df_test = pd.DataFrame(test_data)
    
    # Define user weights for the tasks
    user_weights = {
        "Gaming": 8,
        "ML/AI": 5,
        "HPC": 3,
        "3D Rendering": 6
    }
    
    # For testing, score the test DataFrame.
    df_scored = compute_component_scores_for_df(df_test, user_weights)
    print("Scored Test DataFrame:")
    print(df_scored)
    
    # Example integration: Suppose we have a tuple (GPUs, CPUs, Motherboards, RAMs)
    # Here we simulate motherboards as a DataFrame without any score columns.
    df_mb = pd.DataFrame({
        "Motherboard": ["MB1", "MB2"],
        "Manufacturer": ["ASRock", "Gigabyte"]
    })
    
    # Combine with our test DataFrame (for GPUs, CPUs, RAMs)
    dfs = (df_test, df_test, df_mb, df_test)
    
    scored_dfs = score_all_dfs(dfs, user_weights)
    print("\nScored DataFrames (motherboards remain unchanged):")
    for i, df in enumerate(scored_dfs):
        print(f"DataFrame {i}:")
        print(df, "\n")
