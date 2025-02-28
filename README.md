# PC Builder Prototype

## Program Overview

The PC Builder Prototype is a GUI-based application written in Python that helps users select an optimal combination of PC components (initially GPUs, CPUs, and RAM) based on multiple use-case requirements. The key features of the program include:

- **Database Structure:**  
  The application loads an Excel database where each sheet corresponds to a component type (GPUs, CPUs, and RAMs). Each sheet contains a table of specific components along with their specifications and prices.

- **Component Scoring:**  
  Each component is evaluated in four categories: **Gaming**, **ML/AI**, **HPC**, and **3D Rendering**. The scoring is performed by comparing each component against a baseline product (typically the oldest or the worst-performing model, with all scores set to 1).  
  The score for each task is computed using a formula of the form:

  Score_task = (Sum over specs [(x_spec / baseline_spec)^(nonlinear_scaling_factor) * weight_spec]) * baseline_score

  Here, the nonlinear scaling factor models the nonlinear improvement of performance with the specification, and the baseline score is 1.

  For RAM, an additional factor is introduced that includes the number of channels of the motherboard. This factor multiplies non-capacity terms during the score summation to model the bonus of single, double or quad configurations.

- **Data Processing:**  
After calculating the raw scores, the data is loaded into Python where:
  - Components with missing prices are omitted.
  - All score columns are normalized to a 0–100 scale.
  - User-defined filters (e.g., minimum VRAM, CPU cores, etc.) are applied.

- **Build Generation & Scoring:**  
The application then generates all possible builds (combinations of one GPU, one CPU, and one RAM). For each build, the following are computed:
  - **Total Price and Total Power Consumption**
  - **Final Build Score:**  
      Calculated as a weighted harmonic mean of the individual component scores. Harmonic mean penalizes differences in component scores, favorizing well-balanced builds.
      The weights for each component are determined by combining user-provided task weights with a relevance matrix (which specifies how important each component type is for each task).
  - **Efficiency Metric:**
      The build’s cost efficiency is computed as the ratio of Build Score to Total Price.

- **Recommendation System:**  
A composite recommendation score is calculated as a weighted combination of:
  - The normalized absolute performance (Build Score) and
  - The normalized efficiency (Score-to-Price Ratio).  
The formula used is:

R = α · (BuildScore / P_max) + (1 – α) · (ScoreToPrice / E_max)

where `α` (ranging from 0 to 1) is a tradeoff parameter (set by the user via a slider) that determines the emphasis between absolute performance and cost efficiency.

- **User Interface:**  
The GUI (built with PyQt) allows the user to:
  - Adjust task weights via sliders.
  - Set a price range and component filters.
  - View a table of recommended builds.
  - (Later) See detailed information on a selected build.

## Module Documentation and Architecture

The project is organized into several modules, each with a specific role:

### 1. `data_loader.py`
- **Purpose:**  
Loads the Excel file containing the component specifications. It reads separate sheets (e.g., "GPUs", "CPUs", "RAMs") into pandas DataFrames.
- **Key Details:**  
- Contains a `TASKS` constant (e.g., `["Gaming", "ML/AI", "HPC", "3D Rendering"]`) used by other modules.
- Provides the function `load_specifications()` that returns the DataFrames.

### 2. `data_preprocessor.py`
- **Purpose:**  
Preprocesses the loaded DataFrames by:
- Dropping rows where the price is missing.
- Normalizing each score column to a 0–100 scale.
- **Key Details:**  
- Uses the task names from `data_loader.py` to generate the expected column names (e.g., `"Gaming Score"`).

### 3. `filters.py`
- **Purpose:**  
Contains functions to apply user-defined filters to each component DataFrame (e.g., filtering GPUs by minimum VRAM or maximum power).
- **Key Details:**  
- Provides individual filter functions for GPUs, CPUs, and RAMs.
- Offers a convenience function `apply_all_filters()` to apply all filters at once.

### 4. `component_scoring.py`
- **Purpose:**  
Computes the weighted task score for each component based on user-provided weights.  
- **Key Details:**  
- Implements `compute_component_score()` which calculates a weighted average for a row.
- Provides `compute_component_scores_for_df()` to apply scoring to an entire DataFrame.
- Offers `score_all_dfs()` to score a tuple of DataFrames (for GPUs, CPUs, and RAMs).

### 5. `build_combinations.py`
- **Purpose:**  
Generates all possible builds (combinations of one GPU, one CPU, and one RAM) and computes build-level metrics.
- **Key Details:**  
- Uses `itertools.product` to create combinations.
- Calculates total price, total power, and a final Build Score (using a weighted harmonic mean).
- Includes a function `filter_builds_by_price()` to filter builds based on user-specified price range.

### 6. `recommendation.py`
- **Purpose:**  
Implements the composite recommendation scoring mechanism.
- **Key Details:**  
- Normalizes the absolute performance (BuildScore) and efficiency (ScoreToPrice) metrics.
- Combines them using a user-defined parameter `α` to produce a final Recommendation Score.
- Returns the builds sorted by this score.

### 7. `gui/main_window.py`
- **Purpose:**  
Provides the main graphical user interface using PyQt.
- **Key Details:**  
- Contains sliders for task weights and spin boxes for price range.
- Offers buttons to open a filter dialog and to generate builds.
- Displays the recommended builds in a table (showing selected columns with rounded scores).
- Coordinates calls to the logic modules (data loading, preprocessing, filtering, scoring, build generation, and recommendation).

### 8. `gui/filters_dialog.py`
- **Purpose:**  
Presents a dialog for the user to input detailed filters for each component type.
- **Key Details:**  
- Collects filter criteria (e.g., minimum VRAM, CPU cores, RAM capacity) and returns them to the main window.

### 9. `main.py`
- **Purpose:**  
Serves as the entry point of the application.
- **Key Details:**  
- Initializes the PyQt application.
- Creates and displays the `MainWindow`.

### How They Connect
1. **Data Flow:**  
 - `main.py` starts the GUI by launching `MainWindow`.
 - `MainWindow` calls `load_specifications()` from `data_loader.py` and then `preprocess_data()` from `data_preprocessor.py`.
 - User-specified filters are applied via functions in `filters.py`.
 - The filtered DataFrames are scored by functions in `component_scoring.py`.
 - `build_combinations.py` then generates build combinations and calculates build-level metrics.
 - Finally, `recommendation.py` computes a composite recommendation score for each build.

2. **User Interaction:**  
 - The GUI (in `gui/main_window.py` and `gui/filters_dialog.py`) collects input from the user (e.g., task weights, price range, filter criteria) and displays the resulting recommended builds.

This modular design allows for easy future expansion (for example, adding motherboards and PSUs) while keeping the logic separated from the user interface.

---



