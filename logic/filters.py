import pandas as pd

def apply_gpu_filters(df, vram_min=None, power_max=None):
    """
    Filters a GPU DataFrame by:
      - VRAM Capacity >= vram_min (if provided)
      - Power <= power_max (if provided)
    
    Args:
        df (pd.DataFrame): The GPU DataFrame.
        vram_min (int, optional): Minimum VRAM capacity in GB.
        power_max (int, optional): Maximum power in watts.

    Returns:
        pd.DataFrame: Filtered GPU DataFrame.
    """
    filtered_df = df.copy()

    if vram_min is not None:
        filtered_df = filtered_df[filtered_df["VRAM Capacity"] >= vram_min]

    if power_max is not None:
        filtered_df = filtered_df[filtered_df["Power"] <= power_max]

    return filtered_df


def apply_cpu_filters(df, cores_min=None, power_max=None, socket=None):
    """
    Filters a CPU DataFrame by:
      - CPU Cores >= cores_min (if provided)
      - Power <= power_max (if provided)
      - CPU Socket == socket (if provided; e.g., 'AM4' or 'AM5')
    
    Args:
        df (pd.DataFrame): The CPU DataFrame.
        cores_min (int, optional): Minimum number of CPU cores.
        power_max (int, optional): Maximum power (TDP).
        socket (str, optional): CPU socket type, e.g. 'AM4' or 'AM5'.

    Returns:
        pd.DataFrame: Filtered CPU DataFrame.
    """
    filtered_df = df.copy()

    if cores_min is not None:
        filtered_df = filtered_df[filtered_df["CPU Cores"] >= cores_min]

    if power_max is not None:
        filtered_df = filtered_df[filtered_df["Power"] <= power_max]

    if socket is not None:
        filtered_df = filtered_df[filtered_df["CPU Socket"] == socket]

    return filtered_df


def apply_ram_filters(df, memory_type=None, capacity_min=None):
    """
    Filters an RAM DataFrame by:
      - Memory Type (DDR) == memory_type (if provided; 4 or 5)
      - Memory Capacity >= capacity_min (if provided)
    
    Args:
        df (pd.DataFrame): The RAM DataFrame.
        memory_type (int, optional): DDR version, e.g. 4 or 5.
        capacity_min (int, optional): Minimum memory capacity in GB.

    Returns:
        pd.DataFrame: Filtered RAM DataFrame.
    """
    filtered_df = df.copy()

    if memory_type is not None:
        filtered_df = filtered_df[filtered_df["Memory Type (DDR)"] == memory_type]

    if capacity_min is not None:
        filtered_df = filtered_df[filtered_df["Memory Capacity"] >= capacity_min]

    return filtered_df


def apply_all_filters(df_gpus, df_cpus, df_rams,
                      gpu_filters=None,
                      cpu_filters=None,
                      ram_filters=None):
    """
    Convenience function to apply all filter sets at once.
    
    Args:
        df_gpus, df_cpus, df_rams (pd.DataFrame): Preprocessed DataFrames.
        gpu_filters (dict, optional): e.g. {"vram_min": 8, "power_max": 300}
        cpu_filters (dict, optional): e.g. {"cores_min": 6, "power_max": 125, "socket": "AM4"}
        ram_filters (dict, optional): e.g. {"memory_type": 4, "capacity_min": 16}
        
    Returns:
        tuple: (filtered_gpus, filtered_cpus, filtered_rams)
    """
    gpu_filters = gpu_filters or {}
    cpu_filters = cpu_filters or {}
    ram_filters = ram_filters or {}

    filtered_gpus = apply_gpu_filters(df_gpus,
                                      vram_min=gpu_filters.get("vram_min"),
                                      power_max=gpu_filters.get("power_max"))

    filtered_cpus = apply_cpu_filters(df_cpus,
                                      cores_min=cpu_filters.get("cores_min"),
                                      power_max=cpu_filters.get("power_max"),
                                      socket=cpu_filters.get("socket"))

    filtered_rams = apply_ram_filters(df_rams,
                                      memory_type=ram_filters.get("memory_type"),
                                      capacity_min=ram_filters.get("capacity_min"))

    return filtered_gpus, filtered_cpus, filtered_rams


if __name__ == "__main__":
    # Example usage / quick test
    from data_loader import load_specifications
    from data_preprocessor import preprocess_data
    
    # 1. Load data
    df_gpus, df_cpus, df_rams = load_specifications()
    
    # 2. Preprocess data
    df_gpus, df_cpus, df_rams = preprocess_data([df_gpus, df_cpus, df_rams])
    
    # 3. Define some example filters
    gpu_filters_example = {"vram_min": 8, "power_max": 300}
    cpu_filters_example = {"cores_min": 12, "power_max": 125, "socket": "AM5"}
    ram_filters_example = {"memory_type": 4, "capacity_min": 16}
    
    # 4. Apply all filters
    filtered_gpus, filtered_cpus, filtered_rams = apply_all_filters(
        df_gpus, df_cpus, df_rams,
        gpu_filters=gpu_filters_example,
        cpu_filters=cpu_filters_example,
        ram_filters=ram_filters_example
    )
    
    # 5. Print the results
    print("Filtered GPUs:")
    print(filtered_cpus[["CPU", "CPU Cores", "CPU Socket", "Power", "Gaming Score", "ML/AI Score", "HPC Score", "3D Rendering Score"]])
