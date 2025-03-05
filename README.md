# PC Builder App Documentation

## Overview
The PC Builder App is a GUI‐based Python application designed to help users select an optimal combination of PC components (CPUs, GPUs, Motherboards, and RAM) based on user-defined requirements and performance priorities. The app loads component specifications from an Excel database, preprocesses and filters the data, scores individual components, and then generates "builds" (complete PC configurations) that satisfy compatibility and performance criteria. Finally, it ranks these builds using a composite recommendation score that balances raw performance with cost efficiency.

## Key Features

### Dynamic Data Loading
The app reads component specifications from an Excel file where each sheet corresponds to a component category (CPUs, GPUs, Motherboards, and RAM). This database includes:
- Performance scores
- Pricing (minimum and maximum)
- Power consumption
- Key compatibility information (such as socket type, PCIe versions, and RAM specifications)

### Data Preprocessing
Loaded data is preprocessed to:
- Normalize performance scores (e.g., Gaming Score, ML/AI Score, HPC Score, 3D Rendering Score) to a 0–100 scale.
- Compute an average price from the minimum and maximum prices.
- Assign unique IDs to each component.
- Convert certain multi-element fields (e.g., PCIe lanes) to a "best slot" value.

### Advanced Filtering
Users can set detailed filters (via the GUI) for each component type. Filters include:
- **CPUs**: Brand, type, series, core count, socket, PCIe version, packaging (box/tray), and cooler inclusion.
- **GPUs**: Brand, series, memory capacity, power, PCIe version, and more.
- **Motherboards**: Manufacturer, form factor, CPU socket, chipset, supported RAM type, maximum capacity, and PCIe slots.
- **RAM**: Manufacturer, RAM type, data rate, capacity, lighting options, etc.

Additionally, the filtering function excludes components whose minimum price exceeds the user’s maximum allowed price. The app provides dynamic filter options based on the unique values in the database.

### Component Scoring
Each component is scored based on multiple use-case scenarios (Gaming, ML/AI, HPC, 3D Rendering). The score is computed as a weighted average, comparing a component’s specs against a baseline model. User-adjustable task weights (set via sliders in the GUI) influence these scores.

### Batched Build Generation
Instead of generating the full Cartesian product (which can be prohibitively large), the app processes builds in batches per CPU. For each CPU:

#### Compatibility Filtering
- **Motherboards**: Filtered based on matching CPU socket and chipset compatibility.
- **GPUs**: GPUs are filtered so that the CPU’s "Direct Lanes" (best slot value) is at least the GPU’s required "Wired Lanes."
- **RAM**: RAM candidates are filtered in two stages:
  - **CPU Compatibility**: The motherboard’s RAM type must be among the CPU’s supported types; also, the RAM’s data rate and capacity must fall within the CPU’s limits.
  - **Motherboard Compatibility**: The RAM’s type must match the motherboard’s supported RAM type, and its data rate and capacity must be within the motherboard’s limits.

#### Cross Joining
The filtered motherboards and GPUs are cross-joined and further filtered based on slot lane requirements. This set is then cross-joined with the filtered RAMs.

#### Aggregation
For each valid build (combination of CPU, MB, GPU, and RAM), composite fields such as:
- Total Price (Price Min and Price Max)
- Total Power
- Leftover CPU Lanes

are calculated.

### Scoring and Ranking
Each CPU batch is processed:
1. Builds are filtered by overall price.
2. Builds are scored using a function that computes a weighted harmonic mean of component scores, applies a PCIe version penalty, and a performance imbalance penalty.
3. Builds are ranked by a composite recommendation score.
4. Within the batch, builds are grouped (e.g., by GPU) and the top *n* builds (e.g., top 10) are selected.

### Final Aggregation
The top builds from each CPU batch are concatenated, and a final recommendation scoring is applied to produce the overall ranked list of builds.

## Recommendation Scoring
The final build score is computed using:
- **Performance Score (P)**: Derived from the weighted harmonic mean of the GPU, CPU, and RAM task scores.
- **Efficiency Score (E)**: Computed as Build Score divided by Price Min.

Both scores are normalized and combined using a trade-off parameter **alpha** (adjustable via the GUI) to produce a composite Recommendation Score. Builds are then sorted based on this score.

## Graphical User Interface (GUI)
Built with PyQt6, the GUI includes:

### Main Window
- Sliders for task weight adjustment
- Alpha parameter slider for performance vs. efficiency trade-off
- Price range selectors (min and max)
- Buttons to open a detailed filters dialog, advanced settings, and an About window
- A table displaying recommended builds

### Filters Dialog
Allows users to select filtering options for each component category using dropdowns, checkboxes, and sliders.

### Build Details Dialog
Displays detailed specifications for each component, including links, product names, and additional specs.

### Advanced Settings and About Dialogs
Provide additional configuration options and information about the application.

## Project Architecture
The project is organized into several modules:

### Logic Modules
- `logic/data_loader.py`: Loads the Excel database into pandas DataFrames.
- `logic/data_preprocessor.py`: Preprocesses data by normalizing scores, computing average prices, and assigning unique IDs.
- `logic/filters.py`: Implements filtering functions for each component category.
- `logic/component_scoring.py`: Computes weighted task scores for individual components.
- `logic/build_scoring.py`: Computes the final build score with penalties for PCIe mismatches and performance imbalances.
- `logic/recommendation.py`: Computes composite recommendation scores for builds.
- `logic/smart_picker.py`: (Optional) Groups similar components to reduce duplication and search space.
- `logic/build_maker.py`: Implements batched build generation per CPU.

### GUI Modules
- `gui/main_window.py`: Main application window.
- `gui/filters_dialog.py`: Filtering options dialog.
- `gui/build_details_dialog.py`: Displays build details.
- `gui/about_dialog.py` & `gui/advanced_settings_dialog.py`: Provide additional information and configuration options.

### Other Files
- `main.py`: The application’s entry point, creating the QApplication and starting the event loop.

## Data Flow
1. **Data Loading & Preprocessing**: Load and preprocess component data from an Excel file.
2. **Filtering**: Apply user-defined filters and early price-based exclusion.
3. **Component Scoring**: Compute individual component scores.
4. **Batched Build Generation**: Generate, filter, score, and rank builds per CPU.
5. **Final Recommendation & Ranking**: Merge top builds and compute final recommendation scores.
6. **GUI Presentation**: Display ranked builds in an interactive table.

## Performance Optimization
- **Early Filtering**: Exclude components by price and compatibility before build generation.
- **Batched Processing**: Process builds in manageable batches per CPU.
- **Vectorized Operations**: Use Pandas vectorized operations for filtering and merging.

## Potential Future Enhancements
- **Multithreading or Multiprocessing**: Parallelizing batched build generation.
- **Lazy Evaluation**: Using generators to yield builds on-demand.
- **Dynamic Database Updates**: Allowing updates from online sources.

## Conclusion
The PC Builder app integrates data loading, preprocessing, filtering, component scoring, and batched build generation to recommend optimal PC builds that balance performance and cost. Its modular design ensures flexibility, maintainability, and scalability for future improvements.

