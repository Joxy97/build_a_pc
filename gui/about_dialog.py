from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QScrollArea, QWidget

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About PC Builder")
        self.resize(1200, 600)
        layout = QVBoxLayout(self)

        # Scrollable area
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        
        # Content widget inside the scroll area
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        about_text = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PC Builder App Documentation</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; }
        h1, h2, h3 { color: #333; }
        ul { margin-left: 20px; }
        code { background-color: #f4f4f4; padding: 2px 5px; border-radius: 5px; }
        pre { background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }
    </style>
</head>
<body>
    <h1>PC Builder App Documentation</h1>

    <h2>Overview</h2>
    <p>The PC Builder App is a GUI-based Python application designed to help users select an optimal combination of PC components based on user-defined requirements and performance priorities.</p>
    
    <h2>Key Features</h2>
    <h3>Dynamic Data Loading</h3>
    <p>The app reads component specifications from an Excel file where each sheet corresponds to a component category:</p>
    <ul>
        <li>Performance scores</li>
        <li>Pricing (minimum and maximum)</li>
        <li>Power consumption</li>
        <li>Key compatibility information</li>
    </ul>

    <h3>Data Preprocessing</h3>
    <p>Loaded data is preprocessed to:</p>
    <ul>
        <li>Normalize performance scores</li>
        <li>Compute an average price</li>
        <li>Assign unique IDs</li>
        <li>Convert multi-element fields to a "best slot" value</li>
    </ul>

    <h3>Advanced Filtering</h3>
    <p>Users can set detailed filters for each component type:</p>
    <ul>
        <li><strong>CPUs</strong>: Brand, type, series, core count, socket, PCIe version, packaging, cooler inclusion</li>
        <li><strong>GPUs</strong>: Brand, series, memory capacity, power, PCIe version</li>
        <li><strong>Motherboards</strong>: Manufacturer, form factor, CPU socket, chipset, RAM type, PCIe slots</li>
        <li><strong>RAM</strong>: Manufacturer, RAM type, data rate, capacity, lighting options</li>
    </ul>

    <h3>Component Scoring</h3>
    <p>Each component is scored based on multiple use-case scenarios (Gaming, ML/AI, HPC, 3D Rendering).</p>

    <h3>Batched Build Generation</h3>
    <p>The app generates PC builds in batches per CPU.</p>
    <h4>Compatibility Filtering</h4>
    <ul>
        <li>Motherboards: Filtered based on matching CPU socket and chipset compatibility</li>
        <li>GPUs: Filtered based on PCIe lane requirements</li>
        <li>RAM: Filtered based on CPU and motherboard compatibility</li>
    </ul>

    <h4>Cross Joining & Aggregation</h4>
    <p>Filtered components are cross-joined and further filtered. Composite fields such as total price and power are computed.</p>

    <h3>Scoring and Ranking</h3>
    <p>Builds are scored using a weighted harmonic mean of component scores, applying penalties where needed.</p>

    <h3>Final Aggregation</h3>
    <p>Top builds from each CPU batch are merged and ranked based on a final recommendation score.</p>

    <h2>Graphical User Interface (GUI)</h2>
    <h3>Main Window</h3>
    <ul>
        <li>Sliders for task weight adjustment</li>
        <li>Alpha parameter slider for performance vs. efficiency trade-off</li>
        <li>Price range selectors</li>
        <li>Buttons for filters, advanced settings, and about section</li>
    </ul>
    
    <h3>Filters Dialog</h3>
    <p>Allows users to set detailed filters using dropdowns, checkboxes, and sliders.</p>

    <h3>Build Details Dialog</h3>
    <p>Displays detailed specifications for each component.</p>

    <h2>Project Architecture</h2>
    <h3>Logic Modules</h3>
    <ul>
        <li><code>logic/data_loader.py</code>: Loads the Excel database.</li>
        <li><code>logic/data_preprocessor.py</code>: Preprocesses data.</li>
        <li><code>logic/filters.py</code>: Implements filtering functions.</li>
        <li><code>logic/component_scoring.py</code>: Computes weighted task scores.</li>
        <li><code>logic/build_scoring.py</code>: Computes final build scores.</li>
        <li><code>logic/recommendation.py</code>: Computes recommendation scores.</li>
        <li><code>logic/build_maker.py</code>: Implements batched build generation.</li>
    </ul>

    <h3>GUI Modules</h3>
    <ul>
        <li><code>gui/main_window.py</code>: Main application window.</li>
        <li><code>gui/filters_dialog.py</code>: Filtering options dialog.</li>
        <li><code>gui/build_details_dialog.py</code>: Displays build details.</li>
        <li><code>gui/about_dialog.py</code>: Provides information.</li>
    </ul>

    <h3>Other Files</h3>
    <ul>
        <li><code>main.py</code>: Entry point of the application.</li>
    </ul>

    <h2>Data Flow</h2>
    <ol>
        <li>Data Loading & Preprocessing</li>
        <li>Filtering</li>
        <li>Component Scoring</li>
        <li>Batched Build Generation</li>
        <li>Final Recommendation & Ranking</li>
        <li>GUI Presentation</li>
    </ol>

    <h2>Performance Optimization</h2>
    <ul>
        <li>Early filtering</li>
        <li>Batched processing</li>
        <li>Vectorized operations</li>
    </ul>

    <h2>Potential Future Enhancements</h2>
    <ul>
        <li>Multithreading or multiprocessing</li>
        <li>Lazy evaluation</li>
        <li>Dynamic database updates</li>
    </ul>

    <h2>Conclusion</h2>
    <p>The PC Builder app integrates multiple functionalities to recommend optimal PC builds based on performance and cost efficiency.</p>
</body>
</html>


        """
        label = QLabel(about_text)
        label.setWordWrap(True)
        scroll_layout.addWidget(label)

        scroll_area.setWidget(scroll_content)

        # Close button
        btn = QPushButton("Close")
        btn.clicked.connect(self.accept)

        layout.addWidget(scroll_area)
        layout.addWidget(btn)
