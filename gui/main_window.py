# gui/main_window.py

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QSlider, QPushButton, QSpinBox, QTableWidget, QTableWidgetItem,
    QAction
)
from PyQt5.QtCore import Qt
from .filters_dialog import FiltersDialog
from .build_details_dialog import BuildDetailsDialog

from logic.data_loader import load_specifications
from logic.data_preprocessor import preprocess_data
from logic.filters import apply_all_filters
from logic.component_scoring import score_all_dfs
from logic.build_combinations import generate_builds, filter_builds_by_price
from logic.recommendation import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PC Builder Prototype")
        
        # Make the window bigger
        self.resize(1000, 700)  # width=1000, height=700
        
        # Sliders for tasks
        self.slider_labels = ["Gaming", "ML/AI", "High Precision Computing", "3D Rendering"]
        self.sliders = {}
        
        # Price Range
        self.price_min_spin = QSpinBox()
        self.price_max_spin = QSpinBox()
        self.price_min_spin.setRange(0, 100000)
        self.price_max_spin.setRange(0, 100000)
        self.price_min_spin.setValue(500)
        self.price_max_spin.setValue(2000)
        
        # Main Widget & Layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Task Sliders Layout
        sliders_layout = QHBoxLayout()
        for label_text in self.slider_labels:
            vbox = QVBoxLayout()
            label = QLabel(label_text)
            slider = QSlider(Qt.Vertical)
            slider.setRange(0, 10)
            slider.setValue(5)
            slider.setTickPosition(QSlider.TicksBelow)
            slider.setTickInterval(1)
            self.sliders[label_text] = slider
            vbox.addWidget(label)
            vbox.addWidget(slider)
            sliders_layout.addLayout(vbox)
        main_layout.addLayout(sliders_layout)
        
        # Price Range Layout
        price_layout = QHBoxLayout()
        price_layout.addWidget(QLabel("Min Price"))
        price_layout.addWidget(self.price_min_spin)
        price_layout.addWidget(QLabel("Max Price"))
        price_layout.addWidget(self.price_max_spin)
        main_layout.addLayout(price_layout)
        
        # Filters Button
        self.filters_button = QPushButton("Filters")
        self.filters_button.clicked.connect(self.open_filters_dialog)
        main_layout.addWidget(self.filters_button)
        
        # Build Button
        self.build_button = QPushButton("Build")
        self.build_button.clicked.connect(self.on_build_clicked)
        main_layout.addWidget(self.build_button)
        
        # Results Table
        self.results_table = QTableWidget()
        main_layout.addWidget(self.results_table)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Optional: Action to show build details (if implemented)
        details_action = QAction("Show Details", self)
        details_action.triggered.connect(self.show_build_details)
        self.addAction(details_action)
        
        # Data placeholders
        self.gpus = None
        self.cpus = None
        self.rams = None
        self.filtered_gpus = None
        self.filtered_cpus = None
        self.filtered_rams = None
        self.builds_df = None
        
        # Load and preprocess data on startup
        self.load_and_preprocess_data()
        
        # We'll store filter settings in a dict
        self.gpu_filters = {}
        self.cpu_filters = {}
        self.ram_filters = {}
    
    def load_and_preprocess_data(self):
        # Load
        self.gpus, self.cpus, self.rams = load_specifications()
        # Preprocess
        self.gpus, self.cpus, self.rams = preprocess_data([self.gpus, self.cpus, self.rams])
    
    def open_filters_dialog(self):
        # Open the filters dialog
        dialog = FiltersDialog(self)
        if dialog.exec_() == dialog.Accepted:
            # Retrieve filter settings from the dialog
            self.gpu_filters, self.cpu_filters, self.ram_filters = dialog.get_filters()
    
    def on_build_clicked(self):
        # 1. Apply filters
        self.filtered_gpus, self.filtered_cpus, self.filtered_rams = apply_all_filters(
            self.gpus, self.cpus, self.rams,
            gpu_filters=self.gpu_filters,
            cpu_filters=self.cpu_filters,
            ram_filters=self.ram_filters
        )
        
        # 2. Score each component
        user_weights = {}
        for label_text in self.slider_labels:
            user_weights[label_text] = self.sliders[label_text].value()
        
        scored_gpus, scored_cpus, scored_rams = score_all_dfs(
            (self.filtered_gpus, self.filtered_cpus, self.filtered_rams), 
            user_weights
        )
        
        # 3. Generate all builds
        relevance_matrix = {
            "GPU": {"Gaming":0.5, "ML/AI":0.4, "HPC":0.2, "3D Rendering":0.4},
            "CPU": {"Gaming":0.3, "ML/AI":0.3, "HPC":0.5, "3D Rendering":0.3},
            "RAM": {"Gaming":0.2, "ML/AI":0.3, "HPC":0.3, "3D Rendering":0.3}
        }
        self.builds_df = generate_builds(
            (scored_gpus, scored_cpus, scored_rams),
            user_weights,
            relevance_matrix
        )
        
        # 4. Price Range Filter
        min_price = self.price_min_spin.value()
        max_price = self.price_max_spin.value()
        self.builds_df = filter_builds_by_price(self.builds_df, min_price, max_price)
        
        # 5. Composite Recommendation Score (optional)
        alpha = 0.6  # or read from another slider
        self.builds_df = compute_composite_recommendation_score(self.builds_df, alpha)
        self.builds_df = filter_top_in_group(self.builds_df, ["GPU", "CPU"], score_col="RecommendationScore")
        
        # 6. Show results in table
        self.show_builds_in_table()
    
    def show_builds_in_table(self):
        if self.builds_df is None or self.builds_df.empty:
            self.results_table.setRowCount(0)
            self.results_table.setColumnCount(0)
            return
        
        # Only show these columns
        columns = ["GPU", "CPU", "RAM", "TotalPower", "TotalPrice", "BuildScore", "RecommendationScore"]
        # Filter out any that don't exist
        columns = [col for col in columns if col in self.builds_df.columns]
        
        self.results_table.setColumnCount(len(columns))
        self.results_table.setRowCount(len(self.builds_df))
        self.results_table.setHorizontalHeaderLabels(columns)
        
        for row_idx, (_, row_data) in enumerate(self.builds_df.iterrows()):
            for col_idx, col_name in enumerate(columns):
                value = row_data[col_name]
                
                # Round BuildScore & RecommendationScore to 2 decimals
                if col_name in ["BuildScore", "RecommendationScore"]:
                    value = round(value, 2)
                
                item = QTableWidgetItem(str(value))
                self.results_table.setItem(row_idx, col_idx, item)
    
    def show_build_details(self):
        # (Optional) On selected row, open a dialog with more details
        current_row = self.results_table.currentRow()
        if current_row >= 0:
            build_data = self.builds_df.iloc[current_row].to_dict()
            detail_dialog = BuildDetailsDialog(build_data, self)
            detail_dialog.exec_()
