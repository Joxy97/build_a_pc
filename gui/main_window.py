from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton,
    QSpinBox, QTableWidget, QTableWidgetItem, QSplitter, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QAction

from gui.filters_dialog import FiltersDialog
from gui.build_details_dialog import BuildDetailsDialog
from gui.advanced_settings_dialog import AdvancedSettingsDialog
from gui.about_dialog import AboutDialog

from logic.data_loader import load_specifications
from logic.data_preprocessor import preprocess_data
from logic.filters import apply_all_filters
from logic.component_scoring import score_all_dfs
from logic.build_combinations import generate_builds, filter_builds_by_price_range
from logic.recommendation import compute_composite_recommendation_score, filter_top_in_group

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PC Builder Prototype")
        self.resize(1200, 800)
        
        # Create a splitter to divide the main window into results table and details panel.
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side widget: controls and table.
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        
        # Top controls layout.
        controls_layout = QHBoxLayout()
        
        # Task sliders layout.
        self.task_slider_labels = ["Gaming", "ML/AI", "HPC", "3D Rendering"]
        self.task_sliders = {}
        task_slider_layout = QHBoxLayout()
        for label in self.task_slider_labels:
            vbox = QVBoxLayout()
            lbl = QLabel(label)
            slider = QSlider(Qt.Orientation.Vertical)
            slider.setRange(0, 10)
            slider.setValue(5)
            slider.setTickPosition(QSlider.TickPosition.TicksBelow)
            slider.setTickInterval(1)
            self.task_sliders[label] = slider
            vbox.addWidget(lbl)
            vbox.addWidget(slider)
            task_slider_layout.addLayout(vbox)
        controls_layout.addLayout(task_slider_layout)
        
        # Alpha slider layout.
        alpha_layout = QVBoxLayout()
        alpha_label = QLabel("Alpha (Performance vs Efficiency)")
        self.alpha_slider = QSlider(Qt.Orientation.Horizontal)
        self.alpha_slider.setRange(0, 100)
        self.alpha_slider.setValue(70)  # Default 0.70
        self.alpha_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.alpha_slider.setTickInterval(10)
        self.alpha_value_label = QLabel("0.70")
        self.alpha_slider.valueChanged.connect(lambda val: self.alpha_value_label.setText(f"{val/100:.2f}"))
        alpha_layout.addWidget(alpha_label)
        alpha_layout.addWidget(self.alpha_slider)
        alpha_layout.addWidget(self.alpha_value_label)
        controls_layout.addLayout(alpha_layout)
        
        # Price range layout (using two QSpinBoxes).
        price_layout = QVBoxLayout()
        price_label = QLabel("Price Range (based on Price Min)")
        self.price_min_spin = QSpinBox()
        self.price_min_spin.setRange(0, 100000)
        self.price_min_spin.setValue(500)
        self.price_max_spin = QSpinBox()
        self.price_max_spin.setRange(0, 100000)
        self.price_max_spin.setValue(2000)
        price_layout.addWidget(price_label)
        price_layout.addWidget(QLabel("Min Price"))
        price_layout.addWidget(self.price_min_spin)
        price_layout.addWidget(QLabel("Max Price"))
        price_layout.addWidget(self.price_max_spin)
        controls_layout.addLayout(price_layout)
        
        # Buttons layout.
        buttons_layout = QVBoxLayout()
        self.filters_button = QPushButton("Filters")
        self.filters_button.clicked.connect(self.open_filters_dialog)
        self.advanced_button = QPushButton("Advanced Settings")
        self.advanced_button.clicked.connect(self.open_advanced_settings)
        self.about_button = QPushButton("About")
        self.about_button.clicked.connect(self.open_about_dialog)
        self.build_button = QPushButton("Build/Rebuild")
        self.build_button.clicked.connect(self.on_build_clicked)
        buttons_layout.addWidget(self.filters_button)
        buttons_layout.addWidget(self.advanced_button)
        buttons_layout.addWidget(self.about_button)
        buttons_layout.addWidget(self.build_button)
        controls_layout.addLayout(buttons_layout)
        
        left_layout.addLayout(controls_layout)
        
        # Results Table
        self.results_table = QTableWidget()
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.itemSelectionChanged.connect(self.on_table_selection_changed)
        left_layout.addWidget(self.results_table)
        
        left_widget.setLayout(left_layout)
        self.splitter.addWidget(left_widget)
        
        # Right side: Build details panel.
        self.details_panel = QTextEdit()
        self.details_panel.setReadOnly(True)
        self.splitter.addWidget(self.details_panel)
        self.splitter.setSizes([700, 500])
        
        self.setCentralWidget(self.splitter)
        
        # Data placeholders.
        self.gpus = self.cpus = self.mbs = self.rams = None
        self.filtered_gpus = self.filtered_cpus = self.filtered_mbs = self.filtered_rams = None
        self.builds_df = None
        
        # Load and preprocess data on startup.
        self.load_and_preprocess_data()
        
        # Placeholder for filter settings.
        self.gpu_filters = {}
        self.cpu_filters = {}
        self.mb_filters = {}
        self.ram_filters = {}
    
    def load_and_preprocess_data(self):
        from logic.data_loader import load_specifications
        from logic.data_preprocessor import preprocess_data
        self.gpus, self.cpus, self.mbs, self.rams = load_specifications()
        self.gpus, self.cpus, self.mbs, self.rams = preprocess_data([self.gpus, self.cpus, self.mbs, self.rams])
    
    def open_filters_dialog(self):
        from gui.filters_dialog import FiltersDialog
        dialog = FiltersDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.gpu_filters, self.cpu_filters, self.mb_filters, self.ram_filters = dialog.get_filters()
    
    def open_advanced_settings(self):
        from gui.advanced_settings_dialog import AdvancedSettingsDialog
        dialog = AdvancedSettingsDialog(self)
        dialog.exec()
    
    def open_about_dialog(self):
        from gui.about_dialog import AboutDialog
        dialog = AboutDialog(self)
        dialog.exec()
    
    def on_build_clicked(self):
        from logic.filters import apply_all_filters
        from logic.component_scoring import score_all_dfs
        from logic.build_combinations import generate_builds, filter_builds_by_price_range
        from logic.recommendation import compute_composite_recommendation_score, filter_top_in_group
        
        # Apply filters.
        self.filtered_gpus, self.filtered_cpus, self.filtered_mbs, self.filtered_rams = apply_all_filters(
            self.gpus, self.cpus, self.mbs, self.rams,
            gpu_filters=self.gpu_filters,
            cpu_filters=self.cpu_filters,
            mb_filters=self.mb_filters,
            ram_filters=self.ram_filters
        )
        
        # Retrieve user weights from task sliders.
        user_weights = {label: self.task_sliders[label].value() for label in self.task_slider_labels}
        
        # Score each component.
        scored_gpus, scored_cpus, scored_rams = score_all_dfs(
            (self.filtered_gpus, self.filtered_cpus, self.filtered_rams), user_weights
        )
        
        # Generate builds (order: GPUs, CPUs, MBs, RAMs).
        self.builds_df = generate_builds(self.filtered_gpus, self.filtered_cpus, self.filtered_mbs, self.filtered_rams)
        
        # Filter builds by price range (Price Min).
        min_price = self.price_min_spin.value()
        max_price = self.price_max_spin.value()
        self.builds_df = filter_builds_by_price_range(self.builds_df, min_price, max_price)
        
        # Compute composite recommendation score using alpha slider value.
        alpha = self.alpha_slider.value() / 100.0
        self.builds_df = compute_composite_recommendation_score(self.builds_df, alpha)
        self.builds_df = filter_top_in_group(self.builds_df, ["GPU", "CPU"], score_col="Recommendation Score")
        
        # Show builds in table.
        self.show_builds_in_table()
        self.details_panel.clear()
    
    def show_builds_in_table(self):
        if self.builds_df is None or self.builds_df.empty:
            self.results_table.clear()
            self.results_table.setRowCount(0)
            self.results_table.setColumnCount(0)
            return
        
        # Display columns.
        columns = ["GPU", "CPU", "Motherboard", "RAM", "Total Power", "Price Min", "Price Max", "Build Score", "Recommendation Score"]
        self.results_table.setColumnCount(len(columns))
        self.results_table.setRowCount(len(self.builds_df))
        self.results_table.setHorizontalHeaderLabels(columns)
        
        for row_idx, (_, row) in enumerate(self.builds_df.iterrows()):
            for col_idx, col in enumerate(columns):
                value = row[col]
                if col in ["Build Score", "Recommendation Score"]:
                    value = round(value, 2)
                item = QTableWidgetItem(str(value))
                self.results_table.setItem(row_idx, col_idx, item)
    
    def on_table_selection_changed(self):
        current_row = self.results_table.currentRow()
        if current_row >= 0 and self.builds_df is not None:
            build_data = self.builds_df.iloc[current_row].to_dict()
            # Format details in HTML.
            details_html = ""
            for key, value in build_data.items():
                details_html += f"<b>{key}:</b> {value}<br>"
            self.details_panel.setHtml(details_html)

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QDialog
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
