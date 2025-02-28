import pandas as pd

from .settings import *
from .data_loader import *

def preprocess_data(df_list, tasks=TASKS):
    """
    Preprocesses a list of DataFrames by dropping rows with missing prices
    and normalizing each score column to a 0-100 range.
    
    Args:
        df_list (list): List of pandas DataFrames (e.g., [df_gpus, df_cpus, df_rams]).
        score_columns (list): List of column names containing scores to normalize.
        
    Returns:
        list: List of processed DataFrames.
    """
    processed_list = []
    for df in df_list:
        # Drop rows where 'Price' is missing
        df = df.dropna(subset=["Price"]).copy()
        
        # Normalize each score column: score -> (score / max * 100)
        for task in tasks:
            col = task + " Score"
            if col in df.columns:
                col_max = df[col].max()
                # Avoid division by zero
                if pd.notna(col_max) and col_max != 0:
                    df[col] = df[col] / col_max * 100
        processed_list.append(df)
    return processed_list

if __name__ == "__main__":    
    gpus, cpus, rams = load_specifications()
    
    # Preprocess the data for all three components
    gpus, cpus, rams = preprocess_data([gpus, cpus, rams])
    
    print("Processed GPUs:")
    print(cpus[["CPU", "Price", "Gaming Score", "ML/AI Score", "HPC Score", "3D Rendering Score"]])
