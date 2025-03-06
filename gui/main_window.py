from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton, 
    QSpinBox, QTableWidget, QTableWidgetItem, QSplitter, QTextEdit, QDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from gui.filters_dialog import FiltersDialog
from gui.build_details_dialog import BuildDetailsDialog
from gui.advanced_settings_dialog import AdvancedSettingsDialog
from gui.about_dialog import AboutDialog

from logic.backend_main import run_backend

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PC Builder Prototype")
        self.resize(1200, 800)
        
        # Create main layout with splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        
        # Controls layout
        controls_layout = QHBoxLayout()
        
        # Task sliders
        self.task_slider_labels = ["Gaming", "ML/AI", "HPC", "3D Rendering"]
        self.task_sliders = {}
        task_slider_layout = QHBoxLayout()
        for label in self.task_slider_labels:
            vbox = QVBoxLayout()
            lbl = QLabel(label)
            lbl.setFont(QFont("Aptos", 10, QFont.Weight.Bold))
            slider = QSlider(Qt.Orientation.Vertical)
            slider.setRange(0, 10)
            slider.setValue(5)
            slider.setTickPosition(QSlider.TickPosition.TicksBelow)
            slider.setTickInterval(1)
            self.task_sliders[label] = slider
            vbox.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)
            vbox.addWidget(slider, alignment=Qt.AlignmentFlag.AlignCenter)
            task_slider_layout.addLayout(vbox)
        
        controls_layout.addLayout(task_slider_layout)
        
        # Alpha slider
        alpha_layout = QVBoxLayout()
        alpha_label = QLabel("Save Money ←→ Best Score-to-Price")
        alpha_label.setFont(QFont("Aptos", 10, QFont.Weight.Bold))
        self.alpha_slider = QSlider(Qt.Orientation.Horizontal)
        self.alpha_slider.setRange(0, 100)
        self.alpha_slider.setValue(70)
        self.alpha_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.alpha_slider.setTickInterval(1)
        self.alpha_value_label = QLabel("0.70")
        self.alpha_slider.valueChanged.connect(lambda val: self.alpha_value_label.setText(f"{val/100:.2f}"))
        alpha_layout.addWidget(alpha_label)
        alpha_layout.addWidget(self.alpha_slider)
        alpha_layout.addWidget(self.alpha_value_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        controls_layout.addLayout(alpha_layout)
        
        # Price range controls
        price_layout = QVBoxLayout()
        price_label = QLabel("Price Range")
        price_label.setFont(QFont("Aptos", 10, QFont.Weight.Bold))
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
        
        # Buttons layout
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(10)
        self.filters_button = QPushButton("Filters")
        self.filters_button.clicked.connect(self.open_filters_dialog)
        self.advanced_button = QPushButton("Advanced Settings")
        self.advanced_button.clicked.connect(self.open_advanced_settings)
        self.about_button = QPushButton("About")
        self.about_button.clicked.connect(self.open_about_dialog)
        self.build_button = QPushButton("Build/Rebuild")
        self.build_button.clicked.connect(self.on_build_clicked)
        for btn in [self.filters_button, self.advanced_button, self.about_button, self.build_button]:
            btn.setFont(QFont("Aptos", 10, QFont.Weight.Bold))
            buttons_layout.addWidget(btn)
        
        controls_layout.addLayout(buttons_layout)
        left_layout.addLayout(controls_layout)
        
        # Results Table
        self.results_table = QTableWidget()
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.itemSelectionChanged.connect(self.on_table_selection_changed)
        left_layout.addWidget(self.results_table)
        
        left_widget.setLayout(left_layout)
        self.splitter.addWidget(left_widget)
        
        # Details panel
        self.details_panel = QTextEdit()
        self.details_panel.setReadOnly(True)
        self.splitter.addWidget(self.details_panel)
        self.splitter.setSizes([700, 500])
        
        self.setCentralWidget(self.splitter)
        self.builds_df = None
        self.load_and_preprocess_data()
        self.gpu_filters, self.cpu_filters, self.mb_filters, self.ram_filters = {}, {}, {}, {}
    
    def load_and_preprocess_data(self):
        from logic.data_loader import load_specifications
        from logic.data_preprocessor import preprocess_data
        self.gpus, self.cpus, self.mbs, self.rams = load_specifications()
        self.gpus, self.cpus, self.mbs, self.rams = preprocess_data([self.gpus, self.cpus, self.mbs, self.rams])
    
    def open_filters_dialog(self):
        dialog = FiltersDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.gpu_filters, self.cpu_filters, self.mb_filters, self.ram_filters = dialog.get_filters()
    
    def open_advanced_settings(self):
        AdvancedSettingsDialog(self).exec()
    
    def open_about_dialog(self):
        AboutDialog(self).exec()
    
    def on_build_clicked(self):
        alpha = self.alpha_slider.value() / 100.0
        min_price = self.price_min_spin.value()
        max_price = self.price_max_spin.value()
        user_weights = {label: self.task_sliders[label].value() for label in self.task_slider_labels}
        self.builds_df = run_backend(alpha, min_price, max_price, self.gpu_filters, self.cpu_filters, self.mb_filters, self.ram_filters, user_weights)
        self.show_builds_in_table()
        self.details_panel.clear()
    
    def show_builds_in_table(self):
        if self.builds_df is None or self.builds_df.empty:
            self.results_table.clear()
            return
        
        columns = ["GPU", "CPU", "Motherboard", "RAM", "Total Power", "Price Min", "Build Score", "Recommendation Score"]
        self.results_table.setColumnCount(len(columns))
        self.results_table.setHorizontalHeaderLabels(columns)
        self.results_table.setRowCount(len(self.builds_df))
        
        for row_idx, (_, row) in enumerate(self.builds_df.iterrows()):
            for col_idx, col in enumerate(columns):
                item = QTableWidgetItem(str(row[col]))
                self.results_table.setItem(row_idx, col_idx, item)

    def on_table_selection_changed(self):
        current_row = self.results_table.currentRow()
        if current_row >= 0 and self.builds_df is not None:
            build_data = self.builds_df.iloc[current_row].to_dict()
            details_html = ""
            for key, value in build_data.items():
                details_html += f"<b>{key}:</b> {value}<br>"
            self.details_panel.setHtml(details_html)
