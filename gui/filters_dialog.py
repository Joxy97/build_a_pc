# gui/filters_dialog.py

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton

class FiltersDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Component Filters")
        
        layout = QVBoxLayout()
        
        # Example GPU filters
        gpu_layout = QHBoxLayout()
        gpu_layout.addWidget(QLabel("GPU VRAM Min (GB):"))
        self.gpu_vram_min_edit = QLineEdit()
        gpu_layout.addWidget(self.gpu_vram_min_edit)
        
        gpu_layout.addWidget(QLabel("GPU Power Max (W):"))
        self.gpu_power_max_edit = QLineEdit()
        gpu_layout.addWidget(self.gpu_power_max_edit)
        
        layout.addLayout(gpu_layout)
        
        # Example CPU filters
        cpu_layout = QHBoxLayout()
        cpu_layout.addWidget(QLabel("CPU Cores Min:"))
        self.cpu_cores_min_edit = QLineEdit()
        cpu_layout.addWidget(self.cpu_cores_min_edit)
        
        cpu_layout.addWidget(QLabel("CPU Power Max (W):"))
        self.cpu_power_max_edit = QLineEdit()
        cpu_layout.addWidget(self.cpu_power_max_edit)
        
        layout.addLayout(cpu_layout)
        
        # Example RAM filters
        ram_layout = QHBoxLayout()
        ram_layout.addWidget(QLabel("Memory Type (DDR4=4, DDR5=5):"))
        self.ram_type_edit = QLineEdit()
        ram_layout.addWidget(self.ram_type_edit)
        
        ram_layout.addWidget(QLabel("RAM Capacity Min (GB):"))
        self.ram_capacity_min_edit = QLineEdit()
        ram_layout.addWidget(self.ram_capacity_min_edit)
        
        layout.addLayout(ram_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def get_filters(self):
        """
        Return dictionaries for GPU, CPU, and RAM filters.
        """
        gpu_filters = {}
        if self.gpu_vram_min_edit.text():
            gpu_filters["vram_min"] = float(self.gpu_vram_min_edit.text())
        if self.gpu_power_max_edit.text():
            gpu_filters["power_max"] = float(self.gpu_power_max_edit.text())
        
        cpu_filters = {}
        if self.cpu_cores_min_edit.text():
            cpu_filters["cores_min"] = float(self.cpu_cores_min_edit.text())
        if self.cpu_power_max_edit.text():
            cpu_filters["power_max"] = float(self.cpu_power_max_edit.text())
        
        ram_filters = {}
        if self.ram_type_edit.text():
            ram_filters["memory_type"] = float(self.ram_type_edit.text())
        if self.ram_capacity_min_edit.text():
            ram_filters["capacity_min"] = float(self.ram_capacity_min_edit.text())
        
        return gpu_filters, cpu_filters, ram_filters
