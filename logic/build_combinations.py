import itertools
import pandas as pd
from .settings import *

def get_first(x):
    if isinstance(x, list) and len(x) > 0:
        return x[0]
    return x

# ---------------------------
# Compatibility Checks
# ---------------------------
def is_cpu_gpu_compatible(cpu, gpu):
    """
    Hard compatibility check for CPU and GPU:
      - CPU's direct lanes (first element of "Direct Lanes") must be >= GPU's required lanes (first element of "Wired Lanes").
    """
    cpu_direct = get_first(cpu.get("Direct Lanes"))
    gpu_required = get_first(gpu.get("Wired Lanes"))
    if cpu_direct is None or gpu_required is None:
        return False
    if cpu_direct < gpu_required:
        return False
    return True

def is_cpu_mb_compatible(cpu, mb):
    """
    Check CPU–Motherboard compatibility:
      - Their CPU Socket must match.
      - The motherboard's chipset must be in the CPU's "Chipset Compatibility" list.
    """
    if cpu.get("CPU Socket") != mb.get("CPU Socket"):
        return False
    cpu_chipsets = cpu.get("Chipset Compatibility")
    if not isinstance(cpu_chipsets, list):
        cpu_chipsets = [cpu_chipsets]
    if mb.get("Chipset") not in cpu_chipsets:
        return False
    return True

def is_gpu_mb_compatible(gpu, mb):
    """
    Check GPU–Motherboard compatibility:
      - The motherboard's main PCIe slot (first element of "Wired Lanes") must be >= GPU's required lanes.
    """
    mb_wired = get_first(mb.get("Wired Lanes"))
    gpu_required = get_first(gpu.get("Wired Lanes"))
    if mb_wired is None or gpu_required is None:
        return False
    if mb_wired < gpu_required:
        return False
    return True

def is_ram_compatible(cpu, mb, ram):
    """
    Check RAM compatibility given the CPU and Motherboard:
      - The RAM's "RAM Type" must match the motherboard's "RAM Type".
      - The CPU must support that RAM type.
      - The RAM's Data Rate must not exceed the CPU's maximum supported data rate for that type.
      - The RAM's Capacity must be <= min(CPU["Max Capacity"], MB["Max Capacity"]).
    
    If the CPU supports multiple RAM types, we assume the arrays in CPU for "RAM Type" and "Max Data Rate"
    correspond element-wise.
    """
    mb_ram_type = mb.get("RAM Type")
    if mb_ram_type != ram.get("RAM Type"):
        return False
    
    cpu_ram = cpu.get("RAM Type")
    if isinstance(cpu_ram, list):
        if mb_ram_type not in cpu_ram:
            return False
        cpu_max_rates = cpu.get("Max Data Rate")
        try:
            index = cpu_ram.index(mb_ram_type)
            cpu_max_rate = cpu_max_rates[index] if isinstance(cpu_max_rates, list) else cpu_max_rates
        except (ValueError, IndexError):
            return False
    else:
        if cpu_ram != mb_ram_type:
            return False
        cpu_max_rate = cpu.get("Max Data Rate")
    
    if ram.get("Data Rate") > cpu_max_rate:
        return False
    
    if ram.get("Capacity") > min(cpu.get("Max Capacity"), mb.get("Max Capacity")):
        return False
    
    return True

# ---------------------------
# Build Generation
# ---------------------------
def generate_builds(filtered_gpus, filtered_cpus, filtered_mbs, filtered_rams):
    """
    Generates all valid builds from the filtered DataFrames for GPUs, CPUs, Motherboards, and RAMs.
    The process is:
      1. For each CPU–GPU pair (iterating with GPUs first, then CPUs) that satisfy hard compatibility 
         (CPU direct lanes >= GPU required lanes),
      2. For each CPU–GPU pair, select Motherboards that are compatible with both CPU and GPU.
      3. For each (GPU, CPU, MB) triple, select RAM modules that are compatible with both CPU and MB.
      4. For each valid (GPU, CPU, MB, RAM) combination, compute:
            - "Price Min" as the sum of the Price Min values from each component.
            - "Price Max" as the sum of the Price Max values from each component.
            - "Total Power" as the sum of the Power values.
            - "Leftover CPU Lanes" as CPU direct lanes minus GPU required lanes.
            - Also, include the performance scores ("Task Score") as:
              "GPU Score", "CPU Score", and "RAM Score".
    
    Returns:
        pd.DataFrame: A DataFrame with one row per valid build.
    
    Raises:
        ValueError: If no builds are possible with the current filtered components.
    """
    builds = []
    gpu_records = filtered_gpus.to_dict("records")
    cpu_records = filtered_cpus.to_dict("records")
    mb_records  = filtered_mbs.to_dict("records")
    ram_records = filtered_rams.to_dict("records")
    
    for gpu in gpu_records:
        for cpu in cpu_records:
            if not is_cpu_gpu_compatible(cpu, gpu):
                continue
            cpu_direct = get_first(cpu.get("Direct Lanes"))
            gpu_req = get_first(gpu.get("Wired Lanes"))
            leftover_lanes = cpu_direct - gpu_req if cpu_direct is not None and gpu_req is not None else None
            
            for mb in mb_records:
                if not is_cpu_mb_compatible(cpu, mb):
                    continue
                if not is_gpu_mb_compatible(gpu, mb):
                    continue
                for ram in ram_records:
                    if not is_ram_compatible(cpu, mb, ram):
                        continue
                    
                    # Sum Price Min and Price Max from each component.
                    cpu_price_min = cpu.get("Price Min", 0)
                    cpu_price_max = cpu.get("Price Max", 0)
                    gpu_price_min = gpu.get("Price Min", 0)
                    gpu_price_max = gpu.get("Price Max", 0)
                    mb_price_min  = mb.get("Price Min", 0)
                    mb_price_max  = mb.get("Price Max", 0)
                    ram_price_min = ram.get("Price Min", 0)
                    ram_price_max = ram.get("Price Max", 0)
                    
                    total_price_min = cpu_price_min + gpu_price_min + mb_price_min + ram_price_min
                    total_price_max = cpu_price_max + gpu_price_max + mb_price_max + ram_price_max
                    
                    total_power = (
                        cpu.get("Power", 0) +
                        gpu.get("Power", 0) +
                        mb.get("Power", 0) +
                        ram.get("Power", 0)
                    )
                    
                    # Retrieve performance scores from "Task Score"
                    gpu_score = gpu.get("Task Score", 0)
                    cpu_score = cpu.get("Task Score", 0)
                    ram_score = ram.get("Task Score", 0)
                    
                    builds.append({
                        "GPU": gpu.get("GPU") or gpu.get("Name"),
                        "CPU": cpu.get("CPU") or cpu.get("Name"),
                        "Motherboard": mb.get("Motherboard") or mb.get("Name"),
                        "RAM": ram.get("RAM") or ram.get("Name"),
                        "Price Min": total_price_min,
                        "Price Max": total_price_max,
                        "Total Power": total_power,
                        "Leftover CPU Lanes": leftover_lanes,
                        "GPU Score": gpu_score,
                        "CPU Score": cpu_score,
                        "RAM Score": ram_score
                    })
    
    builds_df = pd.DataFrame(builds)
    if builds_df.empty:
        raise ValueError("There are no compatible builds for these filtering criteria.")
    builds_df.sort_values("Price Min", inplace=True)
    return builds_df

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
    if price_filtered_builds.empty:
        raise ValueError("There are no compatible builds within this price range.")
    return price_filtered_builds


# ---------------------------
# Example Test in Main
# ---------------------------
if __name__ == "__main__":
    # For testing, simulate filtered DataFrames with dummy data.
    
    # Dummy GPU records
    df_gpus = pd.DataFrame([
        {
            "GPU": "NVIDIA GeForce RTX 3060",
            "Wired Lanes": [16],
            "PCIe Version": [4],
            "Power": 170,
            "Price Min": 400,
            "Price Max": 450
        },
        {
            "GPU": "NVIDIA GeForce RTX 3060 Ti",
            "Wired Lanes": [16],
            "PCIe Version": [4],
            "Power": 200,
            "Price Min": 600,
            "Price Max": 700
        }
    ])
    
    # Dummy CPU records
    df_cpus = pd.DataFrame([
        {
            "CPU": "AMD Ryzen 9 9950X",
            "Direct Lanes": [28],
            "CPU Socket": "AMD AM5",
            "Chipset Compatibility": ["A620", "B650", "X670"],
            "RAM Type": "DDR5",
            "Max Data Rate": 5600,
            "Max Capacity": 192,
            "Power": 630,
            "Price Min": 1000,
            "Price Max": 1500
        },
        {
            "CPU": "AMD Ryzen 9 PRO 7945",
            "Direct Lanes": [28],
            "CPU Socket": "AMD AM5",
            "Chipset Compatibility": ["A620", "B650", "X670"],
            "RAM Type": "DDR5",
            "Max Data Rate": 5200,
            "Max Capacity": 192,
            "Power": 415,
            "Price Min": 800,
            "Price Max": 1100
        }
    ])
    
    # Dummy Motherboard records
    df_mbs = pd.DataFrame([
        {
            "Motherboard": "ASRock A620M Pro RS",
            "CPU Socket": "AMD AM5",
            "Chipset": "A620",
            "RAM Type": "DDR5",
            "Max Capacity": 256,
            "Modules": 4,
            "Wired Lanes": [16],
            "Power": 106,
            "Price Min": 70,
            "Price Max": 90
        },
        {
            "Motherboard": "ASRock A620M Pro RS WiFi",
            "CPU Socket": "AMD AM5",
            "Chipset": "A620",
            "RAM Type": "DDR5",
            "Max Capacity": 256,
            "Modules": 4,
            "Wired Lanes": [16],
            "Power": 118,
            "Price Min": 80,
            "Price Max": 100
        }
    ])
    
    # Dummy RAM records
    df_rams = pd.DataFrame([
        {
            "RAM": "KF548C38BB-8",
            "RAM Type": "DDR5",
            "Data Rate": 4800,
            "Capacity": 8,
            "Power": 30,
            "Price Min": 25,
            "Price Max": 35
        },
        {
            "RAM": "CMK32GX5M2A4800C40",
            "RAM Type": "DDR5",
            "Data Rate": 4800,
            "Capacity": 32,
            "Power": 85,
            "Price Min": 100,
            "Price Max": 140
        }
    ])
    
    # Generate builds with the new argument order: GPUs, then CPUs, then Motherboards, then RAMs.
    builds_df = generate_builds(df_gpus, df_cpus, df_mbs, df_rams)
    print("Generated Builds:")
    print(builds_df)

    filtered_builds = filter_builds_by_price_range(builds_df)
    print("Filtered Builds by Price Min:")
    print(filtered_builds)

