import re
import pandas as pd

def split_segments(cell):
    """
    Splits the cell string on commas that are not inside parentheses.
    """
    segments = []
    current = []
    paren_count = 0
    for char in cell:
        if char == '(':
            paren_count += 1
        elif char == ')':
            paren_count -= 1
        if char == ',' and paren_count == 0:
            segment = ''.join(current).strip()
            if segment:
                segments.append(segment)
            current = []
        else:
            current.append(char)
    # Append any remaining text as a segment.
    if current:
        segment = ''.join(current).strip()
        if segment:
            segments.append(segment)
    return segments

def parse_pcie_cell(cell):
    """
    Parses a cell string like:
      "2x PCIe 4.0 x16 (1x x16, 1x x4), 1x PCIe 3.0 x16 (x1), 1x PCIe 3.0 x1"
    into three lists:
      - PCIe Version numbers (using the integer part of the version),
      - Physical lanes for each slot,
      - Wired lanes for each slot.
    """
    versions = []
    physicals = []
    wireds = []
    
    # First split the string into top-level segments.
    segments = split_segments(cell)
    
    # Pattern for a segment:
    #   Group 1: count (e.g., "2")
    #   Group 2: PCIe version (e.g., "4.0")
    #   Group 3: physical lanes (e.g., "16")
    #   Group 4 (optional): content inside parentheses (wired lanes info)
    pattern = re.compile(r"(\d+)x\s*PCIe\s*([\d\.]+)\s*x(\d+)(?:\s*\(([^)]*)\))?")
    
    for seg in segments:
        match = pattern.search(seg)
        if not match:
            continue
        
        count = int(match.group(1))
        # Convert version to integer (e.g., "4.0" becomes 4)
        version = int(float(match.group(2)))
        physical = int(match.group(3))
        wired_str = match.group(4)  # may be None if no parentheses
        
        if wired_str:
            # Split wired lanes info on commas.
            wired_entries = [entry.strip() for entry in wired_str.split(',')]
            wired_list = []
            for entry in wired_entries:
                # Look for the pattern: optional "1x " then "x<number>"
                m = re.search(r"(?:\d+x\s*)?x(\d+)", entry)
                if m:
                    wired_list.append(int(m.group(1)))
            # If a single wired value is provided but count > 1, repeat it.
            if len(wired_list) == 1 and count > 1:
                wired_list = wired_list * count
            # If the number of wired entries doesn't match the count, use physical lanes as fallback.
            elif len(wired_list) != count:
                wired_list = [physical] * count
        else:
            # If no wired lanes provided, use physical lanes.
            wired_list = [physical] * count
        
        # Extend our result lists.
        versions.extend([version] * count)
        physicals.extend([physical] * count)
        wireds.extend(wired_list)
    
    return versions, physicals, wireds

def parse_row(cell):
    """
    Wrapper function to handle non-string cells and return a Series of parsed lists.
    """
    if not isinstance(cell, str):
        return pd.Series([[], [], []], index=["PCIe_Version", "Physical_Lanes", "Wired_Lanes"])
    return pd.Series(parse_pcie_cell(cell), index=["PCIe_Version", "Physical_Lanes", "Wired_Lanes"])

def main():
    # Read the Excel file from Sheet 2. If your sheet name is different, adjust accordingly.
    # Note: sheet_name can be an index (0-indexed) or a sheet name.
    df = pd.read_excel(r"C:\Users\jovan\Python Projects\build_a_pc\data\Specifications.xlsx", sheet_name="Sheet2")
    
    # Assume that the PCIe data is in a column named "PCIe_Spec". Adjust the column name if necessary.
    if "PCIe_Spec" not in df.columns:
        raise KeyError("The expected column 'PCIe_Spec' was not found in the Excel sheet.")
    
    # Apply the parser to each cell in the "PCIe_Spec" column.
    parsed = df["PCIe_Spec"].apply(parse_row)
    
    # Combine the parsed columns with the original DataFrame (if needed) or just use the parsed data.
    # Here, we create a new DataFrame with the parsed data.
    output_df = parsed.copy()
    
    # Export the result to a new Excel file.
    output_df.to_excel("PCIe.xlsx", index=False)
    print("Exported parsed data to PCIe.xlsx")
    
main()
