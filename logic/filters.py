import pandas as pd

# ----------------------------------------------------------------------
# Helper Functions for Filtering
# ----------------------------------------------------------------------
def filter_by_categorical(df, column, value):
    """
    Filters a DataFrame by a categorical column.
    If 'value' is a list, keeps rows where the column's value is in that list.
    If 'value' is a single value, keeps rows where the column equals that value.
    """
    if value is None:
        return df
    if isinstance(value, list):
        return df[df[column].isin(value)]
    else:
        return df[df[column] == value]

def filter_by_numeric_range(df, column, value):
    """
    Filters a DataFrame by a numeric column.
    If 'value' is a tuple (min_val, max_val), filters rows within that range.
    If 'value' is a single number, filters rows equal to that number.
    """
    if value is None:
        return df
    if isinstance(value, tuple) and len(value) == 2:
        min_val, max_val = value
        if min_val is not None:
            df = df[df[column] >= min_val]
        if max_val is not None:
            df = df[df[column] <= max_val]
    else:
        df = df[df[column] == value]
    return df

def filter_by_array_first_element(df, column, value):
    """
    Filters a DataFrame where the column is array-like.
    Compares the first element of each list in the column to 'value'.
    If the cell is not a list, it returns the original value.
    """
    if value is None:
        return df

    def get_first(x):
        if isinstance(x, list) and len(x) > 0:
            return x[0]
        return x

    first_vals = df[column].apply(get_first)
    return df[first_vals == value]

# ----------------------------------------------------------------------
# GPU Filtering
# ----------------------------------------------------------------------
def apply_gpu_filters(df, filters=None):
    """
    Filters a GPU DataFrame based on the following columns:
      - 'Brand' (object)
      - 'Series' (object)
      - 'Manufacturer' (object)
      - 'CUDA Ready' (int64)
      - 'Memory Capacity' (int64)
      - 'Power' (int64)
      - 'PCIe Version' (object; may be array-like)
    """
    filters = filters or {}
    filtered_df = df.copy()

    # Categorical filters
    for col in ["Brand", "Series", "Manufacturer"]:
        if col in filters:
            filtered_df = filter_by_categorical(filtered_df, col, filters[col])

    if "CUDA Ready" in filters:
        filtered_df = filter_by_categorical(filtered_df, "CUDA Ready", filters["CUDA Ready"])

    # Numeric filters
    for col in ["Memory Capacity", "Power"]:
        if col in filters:
            filtered_df = filter_by_numeric_range(filtered_df, col, filters[col])

    # Array-like filter for PCIe Version (using the first element)
    if "PCIe Version" in filters:
        filtered_df = filter_by_array_first_element(filtered_df, "PCIe Version", filters["PCIe Version"])

    return filtered_df

# ----------------------------------------------------------------------
# CPU Filtering
# ----------------------------------------------------------------------
def apply_cpu_filters(df, filters=None):
    """
    Filters a CPU DataFrame based on the following columns:
      - 'Brand' (object)
      - 'Type' (object)
      - 'Series' (object)
      - 'Cores' (int64)
      - 'Threads' (int64)
      - 'CPU Socket' (object)
      - 'Direct PCIe Version' (object; may be array-like)
      - 'Packaging' (object)
      - 'Cooler' (object)
    """
    filters = filters or {}
    filtered_df = df.copy()

    for col in ["Brand", "Type", "Series", "CPU Socket"]:
        if col in filters:
            filtered_df = filter_by_categorical(filtered_df, col, filters[col])

    for col in ["Cores", "Threads"]:
        if col in filters:
            filtered_df = filter_by_numeric_range(filtered_df, col, filters[col])

    if "Direct PCIe Version" in filters:
        filtered_df = filter_by_array_first_element(filtered_df, "Direct PCIe Version", filters["Direct PCIe Version"])

    # New filters for Packaging and Cooler
    if "Packaging" in filters:
        filtered_df = filter_by_categorical(filtered_df, "Packaging", filters["Packaging"])
    if "Cooler" in filters:
        filtered_df = filter_by_categorical(filtered_df, "Cooler", filters["Cooler"])

    return filtered_df

# ----------------------------------------------------------------------
# Motherboard Filtering
# ----------------------------------------------------------------------
def apply_mb_filters(df, filters=None):
    """
    Filters a Motherboard DataFrame based on the following columns:
      - 'Manufacturer' (object)
      - 'Form Factor' (object)
      - 'CPU Socket' (object)
      - 'Chipset' (object)
      - 'RAM Type' (object)
      - 'Max Capacity' (int64)
      - 'Modules' (int64)
      - 'PCIe Version' (object; may be array-like)
    """
    filters = filters or {}
    filtered_df = df.copy()

    for col in ["Manufacturer", "Form Factor", "CPU Socket", "Chipset", "RAM Type"]:
        if col in filters:
            filtered_df = filter_by_categorical(filtered_df, col, filters[col])

    for col in ["Max Capacity", "Modules"]:
        if col in filters:
            filtered_df = filter_by_numeric_range(filtered_df, col, filters[col])

    if "PCIe Version" in filters:
        filtered_df = filter_by_array_first_element(filtered_df, "PCIe Version", filters["PCIe Version"])

    return filtered_df

# ----------------------------------------------------------------------
# RAM Filtering
# ----------------------------------------------------------------------
def apply_ram_filters(df, filters=None):
    """
    Filters a RAM DataFrame based on the following columns:
      - 'Manufacturer' (object)
      - 'RAM Type' (object)
      - 'Data Rate' (int64)
      - 'Capacity' (int64)
      - 'Lighting' (object)
    """
    filters = filters or {}
    filtered_df = df.copy()

    for col in ["Manufacturer", "RAM Type", "Lighting"]:
        if col in filters:
            filtered_df = filter_by_categorical(filtered_df, col, filters[col])

    for col in ["Data Rate", "Capacity"]:
        if col in filters:
            filtered_df = filter_by_numeric_range(filtered_df, col, filters[col])

    return filtered_df

# ----------------------------------------------------------------------
# Convenience Function: Apply All Filters
# ----------------------------------------------------------------------
def apply_all_filters(df_gpus, df_cpus, df_mbs, df_rams,
                      gpu_filters=None,
                      cpu_filters=None,
                      mb_filters=None,
                      ram_filters=None):
    """
    Applies filters to all four component DataFrames and returns them.
    Also checks if any filtered DataFrame is empty and raises an error if so.
    """
    filtered_gpus = apply_gpu_filters(df_gpus, gpu_filters)
    filtered_cpus = apply_cpu_filters(df_cpus, cpu_filters)
    filtered_mbs  = apply_mb_filters(df_mbs, mb_filters)
    filtered_rams = apply_ram_filters(df_rams, ram_filters)
    
    # Check for empty DataFrames and raise an error if any is empty.
    if filtered_gpus.empty:
        raise ValueError("No GPU satisfies these criteria.")
    if filtered_cpus.empty:
        raise ValueError("No CPU satisfies these criteria.")
    if filtered_mbs.empty:
        raise ValueError("No Motherboard satisfies these criteria.")
    if filtered_rams.empty:
        raise ValueError("No RAM satisfies these criteria.")
    
    return filtered_gpus, filtered_cpus, filtered_mbs, filtered_rams

# ----------------------------------------------------------------------
# Dynamic Filter Option Generation
# ----------------------------------------------------------------------
def generate_filter_options(df, filter_spec):
    """
    Generates a dictionary of filter options from a DataFrame based on a filter specification.
    
    filter_spec is a dictionary mapping a filter key to a dict with:
      - "column": The column name in the DataFrame.
      - "type": "categorical", "numeric", or "array".
      - For "array", "array_method" can be "first" (default) or "flatten".
    
    For "categorical": returns a sorted list of unique values.
    For "numeric": returns a tuple (min, max).
    For "array" with method "first": returns unique sorted values of the first element.
    """
    options = {}
    for key, spec in filter_spec.items():
        column = spec["column"]
        col_type = spec.get("type", "categorical")
        if col_type == "categorical":
            unique_vals = df[column].dropna().unique().tolist()
            try:
                unique_vals = sorted(unique_vals)
            except TypeError:
                unique_vals = sorted(unique_vals, key=str)
            options[key] = unique_vals
        elif col_type == "numeric":
            min_val = df[column].min()
            max_val = df[column].max()
            options[key] = (min_val, max_val)
        elif col_type == "array":
            method = spec.get("array_method", "first")
            if method == "first":
                def get_first(x):
                    if isinstance(x, list) and len(x) > 0:
                        return x[0]
                    return x
                unique_vals = df[column].apply(get_first).dropna().unique().tolist()
                try:
                    unique_vals = sorted(unique_vals)
                except TypeError:
                    unique_vals = sorted(unique_vals, key=str)
                options[key] = unique_vals
            elif method == "flatten":
                flattened = df[column].dropna().apply(lambda x: x if isinstance(x, list) else [x])
                all_vals = []
                for sublist in flattened:
                    all_vals.extend(sublist)
                try:
                    unique_vals = sorted(set(all_vals))
                except TypeError:
                    unique_vals = sorted(set(all_vals), key=str)
                options[key] = unique_vals
            else:
                unique_vals = df[column].dropna().unique().tolist()
                try:
                    unique_vals = sorted(unique_vals)
                except TypeError:
                    unique_vals = sorted(unique_vals, key=str)
                options[key] = unique_vals
        else:
            unique_vals = df[column].dropna().unique().tolist()
            try:
                unique_vals = sorted(unique_vals)
            except TypeError:
                unique_vals = sorted(unique_vals, key=str)
            options[key] = unique_vals
    return options

# Filter specification dictionaries for each component:
gpu_filter_spec = {
    "Brand": {"column": "Brand", "type": "categorical"},
    "Series": {"column": "Series", "type": "categorical"},
    "Manufacturer": {"column": "Manufacturer", "type": "categorical"},
    "Memory Capacity": {"column": "Memory Capacity", "type": "numeric"},
    "Power": {"column": "Power", "type": "numeric"},
    "CUDA Ready": {"column": "CUDA Ready", "type": "categorical"},
    "PCIe Version": {"column": "PCIe Version", "type": "array", "array_method": "first"}
}

cpu_filter_spec = {
    "Brand": {"column": "Brand", "type": "categorical"},
    "Type": {"column": "Type", "type": "categorical"},
    "Series": {"column": "Series", "type": "categorical"},
    "Cores": {"column": "Cores", "type": "numeric"},
    "Threads": {"column": "Threads", "type": "numeric"},
    "CPU Socket": {"column": "CPU Socket", "type": "categorical"},
    "Direct PCIe Version": {"column": "Direct PCIe Version", "type": "array", "array_method": "first"},
    "Cooler": {"column": "Cooler", "type": "categorical"}
}

mb_filter_spec = {
    "Manufacturer": {"column": "Manufacturer", "type": "categorical"},
    "Form Factor": {"column": "Form Factor", "type": "categorical"},
    "CPU Socket": {"column": "CPU Socket", "type": "categorical"},
    "Chipset": {"column": "Chipset", "type": "categorical"},
    "RAM Type": {"column": "RAM Type", "type": "categorical"},
    "Max Capacity": {"column": "Max Capacity", "type": "numeric"},
    "Modules": {"column": "Modules", "type": "numeric"},
    "PCIe Version": {"column": "PCIe Version", "type": "array", "array_method": "first"}
}

ram_filter_spec = {
    "Manufacturer": {"column": "Manufacturer", "type": "categorical"},
    "RAM Type": {"column": "RAM Type", "type": "categorical"},
    "Data Rate": {"column": "Data Rate", "type": "numeric"},
    "Capacity": {"column": "Capacity", "type": "numeric"},
    "Lighting": {"column": "Lighting", "type": "categorical"}
}

def generate_all_filter_options(df_gpus, df_cpus, df_mbs, df_rams):
    """
    Generates a dictionary with dynamic filter options for all component types.
    
    Returns a dictionary with keys: 'GPUs', 'CPUs', 'MBs', 'RAMs'.
    """
    options = {
        "GPUs": generate_filter_options(df_gpus, gpu_filter_spec),
        "CPUs": generate_filter_options(df_cpus, cpu_filter_spec),
        "MBs": generate_filter_options(df_mbs, mb_filter_spec),
        "RAMs": generate_filter_options(df_rams, ram_filter_spec)
    }
    return options

# ----------------------------------------------------------------------
# Example Test in Main
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # For testing, import the data loader and preprocessor modules.
    from .data_loader import load_specifications
    from .data_preprocessor import preprocess_data

    # 1. Load the data for GPUs, CPUs, Motherboards, and RAMs.
    df_gpus, df_cpus, df_mbs, df_rams = load_specifications()
    df_gpus, df_cpus, df_mbs, df_rams = preprocess_data([df_gpus, df_cpus, df_mbs, df_rams])

    # 2. Define example filters for each category.
    gpu_filters_example = {
        "Brand": "NVIDIA",
        "Series": ["RTX 3000", "RTX 3060"],
        "Manufacturer": "ASUS",
        "Memory Capacity": (8, None),  # Minimum 8GB
        "Power": (None, 300),          # Maximum 300W
        "CUDA Ready": 1,             # 1 for True
        "PCIe Version": 4
    }

    cpu_filters_example = {
        "Brand": "AMD",
        "Type": "Ryzen 9",
        "Series": "9000",
        "Cores": (12, None),         # Minimum 12 cores
        "Threads": (None, None),
        "CPU Socket": "AMD AM5",
        "Direct PCIe Version": 5,
        "Cooler": "yes"
    }

    mb_filters_example = {
        "Manufacturer": "ASRock",
        "Form Factor": "µATX",
        "CPU Socket": "AMD AM5",
        "Chipset": ["A620", "B650"],
        "RAM Type": "DDR5",
        "Max Capacity": (128, None),  # At least 128GB supported
        "Modules": (None, None),
        "PCIe Version": 4
    }

    ram_filters_example = {
        "Manufacturer": "Kingston",
        "RAM Type": "DDR5",
        "Data Rate": (None, 4800),  # Up to 4800
        "Capacity": (8, None),      # Minimum 8GB per module/kit
        "Lighting": None
    }

    # 3. Apply the filters to each component DataFrame.
    filtered_gpus, filtered_cpus, filtered_mbs, filtered_rams = apply_all_filters(
        df_gpus, df_cpus, df_mbs, df_rams,
        gpu_filters=gpu_filters_example,
        cpu_filters=cpu_filters_example,
        mb_filters=mb_filters_example,
        ram_filters=ram_filters_example
    )

    # 4. Print the shapes and a few rows from each filtered DataFrame.
    print("Filtered GPUs:", filtered_gpus.shape)
    print(filtered_gpus.head(), "\n")

    print("Filtered CPUs:", filtered_cpus.shape)
    print(filtered_cpus.head(), "\n")

    print("Filtered Motherboards:", filtered_mbs.shape)
    print(filtered_mbs.head(), "\n")

    print("Filtered RAMs:", filtered_rams.shape)
    print(filtered_rams.head(), "\n")

    # 5. Generate and print dynamic filter options from the complete data.
    options = generate_all_filter_options(df_gpus, df_cpus, df_mbs, df_rams)
    print("Dynamic Filter Options for GPUs:")
    print(options["GPUs"], "\n")
    print("Dynamic Filter Options for CPUs:")
    print(options["CPUs"], "\n")
    print("Dynamic Filter Options for Motherboards:")
    print(options["MBs"], "\n")
    print("Dynamic Filter Options for RAMs:")
    print(options["RAMs"], "\n")
