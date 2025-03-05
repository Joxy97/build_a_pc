import pandas as pd
from .settings import ALPHA, MIN_PRICE, MAX_PRICE, USER_WEIGHTS
from .build_scoring import score_builds
from .recommendation import compute_composite_recommendation_score, filter_top_in_group

def filter_builds_by_price_range(builds_df, min_price=MIN_PRICE, max_price=MAX_PRICE):
    """
    Filters the builds DataFrame by ensuring that the build's Price Min falls within the specified range.
    
    Args:
        builds_df (pd.DataFrame): DataFrame containing builds with a "Price Min" column.
        min_price (float): Minimum acceptable price.
        max_price (float): Maximum acceptable price.
        
    Returns:
        pd.DataFrame: Filtered DataFrame where Price Min is within the given range.
    """
    price_filtered_builds = builds_df[(builds_df["Price Min"] >= min_price) & (builds_df["Price Min"] <= max_price)]
    return price_filtered_builds

def get_first(x):
    """Return the first element if x is a list; otherwise return x."""
    if isinstance(x, list) and len(x) > 0:
        return x[0]
    return x

def namespace_df(df, prefix, exclude_cols=None):
    """
    Renames columns in df by prefixing with prefix, except for those in exclude_cols.
    """
    if exclude_cols is None:
        exclude_cols = []
    df = df.copy()
    new_cols = {col: f"{prefix} {col}" for col in df.columns if col not in exclude_cols}
    return df.rename(columns=new_cols)

def add_best_slot(df, col, new_col):
    """Adds a column new_col containing the first element of the column col."""
    df = df.copy()
    df[new_col] = df[col].apply(get_first)
    return df

def cross_join(df1, df2):
    """Returns the Cartesian product (cross join) of two DataFrames."""
    df1 = df1.copy()
    df2 = df2.copy()
    df1["key"] = 1
    df2["key"] = 1
    merged = pd.merge(df1, df2, on="key")
    merged.drop(columns=["key"], inplace=True)
    return merged

def build_maker_batched(df_gpus, df_cpus, df_mbs, df_rams,
                        min_price=MIN_PRICE, max_price=MAX_PRICE,
                        user_weights=USER_WEIGHTS, top_n=10):
    """
    Batched build generation.
    Input DataFrames use original column names. This function first namespaces each
    DataFrame to avoid key collisions, then processes builds per CPU.
    """
    # Namespace each DataFrame:

    df_gpus = df_gpus[["ID", "GPU", "Power", "PCIe Version", "Wired Lanes", "Price Min", "Price Max", "Task Score"]].copy()
    df_cpus = df_cpus[["ID", "CPU", "CPU Socket", "Chipset Compatibility", "Power", "RAM Type",
                            "Max Capacity", "Max Data Rate", "Direct PCIe Version", "Direct Lanes", "Price Min", "Price Max", "Task Score"]].copy()
    df_mbs = df_mbs[["ID", "Motherboard", "CPU Socket", "Chipset", "RAM Type", "Max Capacity", 
                          "Max Data Rate", "Modules", "PCIe Version", "Wired Lanes", "Price Min", "Price Max",]].copy()
    df_rams = df_rams[["ID", "RAM", "RAM Type", "Data Rate", "Capacity", "Modules", "Price Min", "Price Max", "Task Score"]].copy()

    cpu_df = namespace_df(df_cpus, "CPU", exclude_cols=["CPU"])
    gpu_df = namespace_df(df_gpus, "GPU", exclude_cols=["GPU"])
    mb_df  = namespace_df(df_mbs, "MB",  exclude_cols=["Motherboard"])
    ram_df = namespace_df(df_rams, "RAM", exclude_cols=["RAM"])
        
    # Extract best-slot numeric fields.
    cpu_df = add_best_slot(cpu_df, "CPU Direct Lanes", "CPU Main Direct Lanes")
    cpu_df = add_best_slot(cpu_df, "CPU Direct PCIe Version", "CPU Main Direct PCIe Version")
    gpu_df = add_best_slot(gpu_df, "GPU Wired Lanes", "GPU Main Wired Lanes")
    gpu_df = add_best_slot(gpu_df, "GPU PCIe Version", "GPU Main PCIe Version")
    mb_df  = add_best_slot(mb_df, "MB Wired Lanes",  "MB Main Wired Lanes")
    mb_df  = add_best_slot(mb_df, "MB PCIe Version",  "MB Main PCIe Version")
    # (Assuming column names: "Direct Lanes", "Wired Lanes" etc. Adjust as needed.)
    
    final_builds = []
    
    # Process per CPU.
    for idx, cpu in cpu_df.iterrows():
        print(f"Processing batch for CPU {cpu['CPU']}...")
        
        # 1. Filter MBs: match CPU Socket and check that MB_Chipset is in CPU_Chipset Compatibility.
        mb_candidates = mb_df[mb_df["MB CPU Socket"] == cpu["CPU CPU Socket"]].copy()
        mb_candidates = mb_candidates[mb_candidates.apply(
            lambda row: row["MB Chipset"] in cpu["CPU Chipset Compatibility"], axis=1)]
        if mb_candidates.empty:
            continue
        
        # 2. Filter GPUs: CPU_DirectLanes_best >= GPU_WiredLanes_best.
        gpu_candidates = gpu_df[gpu_df["GPU Main Wired Lanes"] <= cpu["CPU Main Direct Lanes"]].copy()
        if gpu_candidates.empty:
            continue
        
        
        # 3. Filter RAMs: RAM RAM Type is in CPU RAM Type (stores matched indices), CPU Max Capacity >= RAM Capacity AND CPU Max Data Rate >= RAM Data Rate based on the stored index.
        ram_candidates = ram_df[ram_df.apply(
            lambda row: row["RAM RAM Type"] in cpu["CPU RAM Type"], axis=1)].copy()
        ram_candidates.loc[:, "Matching Index"] = ram_candidates["RAM RAM Type"].apply(
            lambda ram_type: cpu["CPU RAM Type"].index(ram_type) if ram_type in cpu["CPU RAM Type"] else None
        )
        ram_candidates = ram_candidates[ram_candidates["RAM Capacity"] <= cpu["CPU Max Capacity"]]
        ram_candidates = ram_candidates[
            ram_candidates.apply(lambda row: row["RAM Data Rate"] <= cpu["CPU Max Data Rate"][row["Matching Index"]]
                                 if row["Matching Index"] is not None else False, axis=1)
        ]

        # Drop the temporary "Matching Index" column if no longer needed
        ram_candidates = ram_candidates.drop(columns=["Matching Index"])
        
        
        # 4. Cross join MBs and GPUs and filter: MB_WiredLanes_best >= GPU_WiredLanes_best.
        mb_candidates["key"] = 1
        gpu_candidates["key"] = 1
        mb_gpu = pd.merge(mb_candidates, gpu_candidates, on="key")
        mb_gpu.drop(columns=["key"], inplace=True)
        mb_gpu = mb_gpu[mb_gpu["MB Main Wired Lanes"] >= mb_gpu["GPU Main Wired Lanes"]]
        if mb_gpu.empty:
            continue
        
        # 4. Cross join with RAMs.
        mb_gpu["key"] = 1
        ram_candidates["key"] = 1
        batch_builds = pd.merge(mb_gpu, ram_candidates, on="key")
        batch_builds.drop(columns=["key"], inplace=True)
        batch_builds = batch_builds[batch_builds["MB RAM Type"] == batch_builds["RAM RAM Type"]]
        batch_builds = batch_builds[batch_builds["MB Max Capacity"] >= batch_builds["RAM Capacity"]]
        batch_builds = batch_builds[batch_builds["MB Max Data Rate"] >= batch_builds["RAM Data Rate"]]
        
        # 5. Inject current CPU info into batch.
        for col in cpu_df.columns:
            batch_builds[col] = [cpu[col]] * len(batch_builds)
        
        # 6. Compute aggregated fields.
        batch_builds["Price Min"] = (
            batch_builds["CPU Price Min"] +
            batch_builds["MB Price Min"] +
            batch_builds["GPU Price Min"] +
            batch_builds["RAM Price Min"]
        )
        batch_builds["Price Max"] = (
            batch_builds["CPU Price Max"] +
            batch_builds["MB Price Max"] +
            batch_builds["GPU Price Max"] +
            batch_builds["RAM Price Max"]
        )
        # 7. Total Power from CPU, MB, GPU only (RAM typically does not contribute power).
        batch_builds["Total Power"] = (
            batch_builds["CPU Power"] +
            batch_builds["GPU Power"]
        )
        batch_builds["Leftover CPU Lanes"] = (
            batch_builds["CPU Main Direct Lanes"] - batch_builds["GPU Main Wired Lanes"]
        ).clip(lower=0)
        
        # 8. Process the batch:
        batch_builds = batch_builds[["GPU", "CPU", "Motherboard", "RAM", "Total Power", "GPU Task Score", "CPU Task Score", "RAM Task Score", "CPU Main Direct PCIe Version", "GPU Main PCIe Version", "MB Main PCIe Version", "Leftover CPU Lanes", "Price Min", "Price Max", "GPU ID", "CPU ID", "MB ID", "RAM ID"]]
        filtered_batch = filter_builds_by_price_range(batch_builds, min_price, max_price)
        if filtered_batch.empty:
            continue

        scored_batch = score_builds(filtered_batch, user_weights)
        batch_rec = compute_composite_recommendation_score(scored_batch, alpha=user_weights.get("alpha", 0.7))
        # Group by GPU (since CPU is fixed) and pick top_n builds.
        grouped_batch = filter_top_in_group(batch_rec, ["GPU"], score_col="Recommendation Score")
        top_builds = grouped_batch.head(top_n).copy()
        # Drop temporary recommendation columns.
        for col in ["Recommendation Score", "Normalized Performance", "Normalized Efficiency", "Score To Price"]:
            if col in top_builds.columns:
                top_builds.drop(columns=[col], inplace=True)
        final_builds.append(top_builds)
    
    if not final_builds:
        raise ValueError("There are no possible builds with components that satisfy these criteria.")
    
    final_df = pd.concat(final_builds, ignore_index=True)
    # Final recommendation scoring on the full final DataFrame.
    final_df = compute_composite_recommendation_score(final_df, alpha=user_weights.get("alpha", 0.7))
    final_df = filter_top_in_group(final_df, ["GPU", "CPU"], score_col="Recommendation Score")
    final_df.sort_values("Recommendation Score", inplace=True)
    final_df.reset_index(drop=True, inplace=True)
    return final_df
