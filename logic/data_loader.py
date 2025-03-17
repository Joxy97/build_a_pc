import pandas as pd
from .settings import EXCEL_PATH

def parse_array(value, type_func=str):
    """
    Converts a cell value to a list.
    If the value is a string, it splits on commas and applies type_func.
    Otherwise, returns a one-element list with the value.
    """
    if pd.isna(value):
        return []
    if isinstance(value, str):
        # Split by comma and strip whitespace
        parts = [part.strip() for part in value.split(",")]
        try:
            return [type_func(part) for part in parts]
        except ValueError:
            # If conversion fails, return as string list
            return parts
    return [value]

def convert_columns_to_array(df, col_info):
    """
    Given a DataFrame and a dictionary mapping column names to conversion functions,
    convert those columns to array-like lists.
    
    Args:
        df (pd.DataFrame): The DataFrame to modify.
        col_info (dict): Mapping of column names to a type conversion function (e.g., float, str).
    Returns:
        pd.DataFrame: The modified DataFrame.
    """
    for col, type_func in col_info.items():
        if col in df.columns:
            df[col] = df[col].apply(lambda x: parse_array(x, type_func))
    return df

def load_specifications(excel_path=EXCEL_PATH):
    """
    Loads specifications for GPUs, CPUs, Motherboards, and RAMs from the given Excel file.
    
    Args:
        excel_path (str): Path to the Excel file.
        
    Returns:
        tuple: Four pandas DataFrames for GPUs, CPUs, Motherboards, and RAMs respectively.
    """
    # Adjust the usecols and skiprows as per your updated Excel layout.
    df_gpus = pd.read_excel(excel_path, sheet_name="GPUs", skiprows=7, usecols="A:AF")
    df_cpus = pd.read_excel(excel_path, sheet_name="CPUs", skiprows=7, usecols="A:AF", dtype={"Series": str})
    df_mbs  = pd.read_excel(excel_path, sheet_name="MBs", skiprows=7, usecols="A:S")
    df_rams = pd.read_excel(excel_path, sheet_name="RAMs", skiprows=7, usecols="A:S")
    
    # Define which columns should be treated as array-like and their conversion type.
    gpu_array_cols = {
        "PCIe Version": int,
        "Physical Lanes": int,
        "Wired Lanes": int
    }
    
    cpu_array_cols = {
        "Chipset Compatibility": str,
        "RAM Type": str,
        "Max Data Rate": int,  # or float if some values are fractional
        "Direct PCIe Version": int,
        "Direct Lanes": int,
        "Interface PCIe Version": int,
        "Interface Lanes": int
    }
    
    mb_array_cols = {
        "PCIe Version": int,
        "Physical Lanes": int,
        "Wired Lanes": int
    }
    
    # Convert specified columns to array-like structures
    df_gpus = convert_columns_to_array(df_gpus, gpu_array_cols)
    df_cpus = convert_columns_to_array(df_cpus, cpu_array_cols)
    df_mbs  = convert_columns_to_array(df_mbs, mb_array_cols)
    
    return df_gpus, df_cpus, df_mbs, df_rams

def load_specifications_products(excel_path=EXCEL_PATH):
    """
    Loads specifications for GPUs, CPUs, Motherboards, and RAMs from the given Excel file.
    
    Args:
        excel_path (str): Path to the Excel file.
        
    Returns:
        tuple: Four pandas DataFrames for GPUs, CPUs, Motherboards, and RAMs respectively.
    """
    # Adjust the usecols and skiprows as per your updated Excel layout.
    df_gpus = pd.read_excel(excel_path, sheet_name="GPUs Products", skiprows=7, usecols="A:AF")
    df_cpus = pd.read_excel(excel_path, sheet_name="CPUs Products", skiprows=7, usecols="A:AF", dtype={"Series": str})
    df_mbs  = pd.read_excel(excel_path, sheet_name="MBs Products", skiprows=7, usecols="A:S")
    df_rams = pd.read_excel(excel_path, sheet_name="RAMs Products", skiprows=7, usecols="A:S")
    
    # Define which columns should be treated as array-like and their conversion type.
    gpu_array_cols = {
        "PCIe Version": int,
        "Physical Lanes": int,
        "Wired Lanes": int
    }
    
    cpu_array_cols = {
        "Chipset Compatibility": str,
        "RAM Type": str,
        "Max Data Rate": int,  # or float if some values are fractional
        "Direct PCIe Version": int,
        "Direct Lanes": int,
        "Interface PCIe Version": int,
        "Interface Lanes": int
    }
    
    mb_array_cols = {
        "PCIe Version": int,
        "Physical Lanes": int,
        "Wired Lanes": int
    }
    
    # Convert specified columns to array-like structures
    df_gpus = convert_columns_to_array(df_gpus, gpu_array_cols)
    df_cpus = convert_columns_to_array(df_cpus, cpu_array_cols)
    df_mbs  = convert_columns_to_array(df_mbs, mb_array_cols)
    
    return df_gpus, df_cpus, df_mbs, df_rams

if __name__ == "__main__":
    dfs = load_specifications()
    names = ["GPUs", "CPUs", "MBs", "RAMs"]
    for name, df in zip(names, dfs):
        print(f"--- {name} ---")
        # Print a subset of columns (e.g., performance scores for GPUs/CPUs, or key columns for Motherboards)
        if name == "GPUs":
            print(df.columns)
        elif name == "CPUs":
            print(df.columns)
        elif name == "MBs":
            print(df.columns)
        elif name == "RAMs":
            print(df.columns)
