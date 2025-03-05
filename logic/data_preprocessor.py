import pandas as pd
from .settings import TASKS
from .data_loader import load_specifications

def preprocess_data(df_list, tasks=TASKS):
    """
    Preprocesses a list of DataFrames by:
      - Adding a unique "ID" column (starting at 1) to each DataFrame.
      - Computing an average price ("Avg Price") as the mean of "Price Min" and "Price Max" if available.
      - Normalizing each score column to a 0-100 range.
    
    Args:
        df_list (list): List of pandas DataFrames (e.g., [df_gpus, df_cpus, df_mbs, df_rams]).
        tasks (list): List of tasks for which scores should be normalized.
        
    Returns:
        list: List of processed DataFrames.
    """
    processed_list = []
    for df in df_list:
        # Insert a unique ID column starting from 1.
        df.insert(0, "ID", range(1, len(df) + 1))
        
        # Compute an average price from 'Price Min' and 'Price Max' if those columns exist.
        if "Price Min" in df.columns and "Price Max" in df.columns:
            df["Avg Price"] = (df["Price Min"] + df["Price Max"]) / 2
        
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
    # Load data for all four component types (GPUs, CPUs, Motherboards, RAMs)
    gpus, cpus, mbs, rams = load_specifications()
    
    # Preprocess the data for all components (ID column will be added here)
    gpus, cpus, mbs, rams = preprocess_data([gpus, cpus, mbs, rams])
    
    print("Processed GPUs:")
    print(gpus[["ID", "Gaming Score", "ML/AI Score", "HPC Score", "3D Rendering Score", "Avg Price"]].head())
    print("Processed CPUs:")
    print(cpus[["ID", "Gaming Score", "ML/AI Score", "HPC Score", "3D Rendering Score", "Avg Price"]].head())
