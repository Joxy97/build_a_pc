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
        
    numerator = 0
    denominator = 0
    for task, weight in user_weights.items():
        col_name = task + " Score"
        if col_name and col_name in row:
            numerator += weight * row[col_name]
            denominator += weight
    return numerator / denominator if denominator else 0


def compute_component_scores_for_df(df, user_weights):
    """
    Applies the weighted score calculation to every row in the DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame containing component data.
        user_weights (dict): Dictionary with task names and user-provided weights.
        score_columns (dict, optional): Mapping of task names to DataFrame column names.
    
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
    Applies the weighted score calculation for all dataframes.
    
    Args:
        filtered_dfs (tuple): A tuple of DataFrames (usually filtered DataFrames)
                              in the order (GPUs, CPUs, RAMs).
        user_weights (dict): Dictionary with task names and user-provided weights.
        score_columns (dict, optional): Mapping of task names to DataFrame column names.
    
    Returns:
        tuple: (scored_gpus, scored_cpus, scored_rams): A tuple of scored DataFrames.
    """
    scored_dfs = tuple(
        compute_component_scores_for_df(df, user_weights)
        for df in filtered_dfs
    )
    return scored_dfs



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
    
    df_scored = score_all_dfs((df_test,), user_weights)
    print(df_scored)
