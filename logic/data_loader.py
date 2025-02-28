import pandas as pd

from .settings import *

def load_specifications(excel_path = EXCEL_PATH):
    """
    Loads specifications for GPUs, CPUs, and RAMs from the given Excel file.
    
    Args:
        excel_path (str): Path to the Excel file.
        
    Returns:
        tuple: Three pandas DataFrames for GPUs, CPUs, and RAMs respectively.
    """
    df_gpus = pd.read_excel(excel_path, sheet_name="GPUs", skiprows=7, usecols="A:S")
    df_cpus = pd.read_excel(excel_path, sheet_name="CPUs", skiprows=7, usecols="A:Y")
    df_rams = pd.read_excel(excel_path, sheet_name="RAMs", skiprows=7, usecols="A:L")
    return df_gpus, df_cpus, df_rams

if __name__ == "__main__":
    dfs = load_specifications()
    for df in dfs:
        print(df[["Gaming Score", "ML/AI Score", "HPC Score", "3D Rendering Score"]])
