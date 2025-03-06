from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTabWidget, QWidget, QFormLayout,
    QLabel, QLineEdit, QComboBox, QSpinBox, QPushButton, QHBoxLayout
)
from PyQt6.QtCore import Qt

# Adjust these imports to match your project structure:
from logic.data_loader import load_specifications
from logic.data_preprocessor import preprocess_data
from logic.filters import generate_all_filter_options

class FiltersDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Component Filters")
        self.resize(600, 400)
        
        layout = QVBoxLayout(self)
        tabs = QTabWidget()

        # --------------------- GPU Tab ---------------------
        self.gpu_tab = QWidget()
        gpu_layout = QFormLayout()

        self.gpu_brand_combo = QComboBox()
        self.gpu_brand_combo.setEditable(True)
        gpu_layout.addRow("Brand:", self.gpu_brand_combo)

        self.gpu_series_combo = QComboBox()
        self.gpu_series_combo.setEditable(True)
        gpu_layout.addRow("Series:", self.gpu_series_combo)

        self.gpu_manufacturer_combo = QComboBox()
        self.gpu_manufacturer_combo.setEditable(True)
        gpu_layout.addRow("Manufacturer:", self.gpu_manufacturer_combo)

        self.gpu_vram_min_edit = QLineEdit()
        gpu_layout.addRow("Memory Capacity Min (GB):", self.gpu_vram_min_edit)

        self.gpu_power_max_edit = QLineEdit()
        gpu_layout.addRow("Power Max (W):", self.gpu_power_max_edit)

        self.gpu_pcie_version_combo = QComboBox()
        self.gpu_pcie_version_combo.setEditable(True)
        gpu_layout.addRow("PCIe Version:", self.gpu_pcie_version_combo)

        self.gpu_cuda_ready_combo = QComboBox()
        # We’ll addItems() dynamically, but let's keep a default blank:
        self.gpu_cuda_ready_combo.setEditable(True)
        gpu_layout.addRow("CUDA Ready:", self.gpu_cuda_ready_combo)

        self.gpu_tab.setLayout(gpu_layout)
        tabs.addTab(self.gpu_tab, "GPU")

        # --------------------- CPU Tab ---------------------
        self.cpu_tab = QWidget()
        cpu_layout = QFormLayout()

        self.cpu_brand_combo = QComboBox()
        self.cpu_brand_combo.setEditable(True)
        cpu_layout.addRow("Brand:", self.cpu_brand_combo)

        self.cpu_type_combo = QComboBox()
        self.cpu_type_combo.setEditable(True)
        cpu_layout.addRow("Type:", self.cpu_type_combo)

        self.cpu_series_combo = QComboBox()
        self.cpu_series_combo.setEditable(True)
        cpu_layout.addRow("Series:", self.cpu_series_combo)

        self.cpu_cores_min_spin = QSpinBox()
        self.cpu_cores_min_spin.setRange(0, 64)
        cpu_layout.addRow("Cores Min:", self.cpu_cores_min_spin)

        self.cpu_threads_min_spin = QSpinBox()
        self.cpu_threads_min_spin.setRange(0, 128)
        cpu_layout.addRow("Threads Min:", self.cpu_threads_min_spin)

        self.cpu_socket_combo = QComboBox()
        self.cpu_socket_combo.setEditable(True)
        cpu_layout.addRow("CPU Socket:", self.cpu_socket_combo)

        self.cpu_direct_pcie_combo = QComboBox()
        self.cpu_direct_pcie_combo.setEditable(True)
        cpu_layout.addRow("Direct PCIe Version:", self.cpu_direct_pcie_combo)

        self.cpu_packaging_combo = QComboBox()
        self.cpu_packaging_combo.setEditable(True)
        cpu_layout.addRow("Packaging:", self.cpu_packaging_combo)

        self.cpu_cooler_combo = QComboBox()
        self.cpu_cooler_combo.setEditable(True)
        cpu_layout.addRow("Cooler:", self.cpu_cooler_combo)

        self.cpu_tab.setLayout(cpu_layout)
        tabs.addTab(self.cpu_tab, "CPU")

        # --------------------- Motherboard Tab ---------------------
        self.mb_tab = QWidget()
        mb_layout = QFormLayout()

        self.mb_manufacturer_combo = QComboBox()
        self.mb_manufacturer_combo.setEditable(True)
        mb_layout.addRow("Manufacturer:", self.mb_manufacturer_combo)

        self.mb_form_factor_combo = QComboBox()
        self.mb_form_factor_combo.setEditable(True)
        mb_layout.addRow("Form Factor:", self.mb_form_factor_combo)

        self.mb_cpu_socket_combo = QComboBox()
        self.mb_cpu_socket_combo.setEditable(True)
        mb_layout.addRow("CPU Socket:", self.mb_cpu_socket_combo)

        self.mb_chipset_combo = QComboBox()
        self.mb_chipset_combo.setEditable(True)
        mb_layout.addRow("Chipset:", self.mb_chipset_combo)

        self.mb_ram_type_combo = QComboBox()
        self.mb_ram_type_combo.setEditable(True)
        mb_layout.addRow("RAM Type:", self.mb_ram_type_combo)

        self.mb_max_capacity_spin = QSpinBox()
        self.mb_max_capacity_spin.setRange(0, 1024)
        mb_layout.addRow("Max Capacity (GB):", self.mb_max_capacity_spin)

        self.mb_modules_spin = QSpinBox()
        self.mb_modules_spin.setRange(0, 16)
        mb_layout.addRow("Modules:", self.mb_modules_spin)

        self.mb_pcie_version_combo = QComboBox()
        self.mb_pcie_version_combo.setEditable(True)
        mb_layout.addRow("PCIe Version:", self.mb_pcie_version_combo)

        self.mb_tab.setLayout(mb_layout)
        tabs.addTab(self.mb_tab, "Motherboard")

        # --------------------- RAM Tab ---------------------
        self.ram_tab = QWidget()
        ram_layout = QFormLayout()

        self.ram_manufacturer_combo = QComboBox()
        self.ram_manufacturer_combo.setEditable(True)
        ram_layout.addRow("Manufacturer:", self.ram_manufacturer_combo)

        self.ram_type_combo = QComboBox()
        self.ram_type_combo.setEditable(True)
        ram_layout.addRow("RAM Type:", self.ram_type_combo)

        self.ram_data_rate_spin = QSpinBox()
        self.ram_data_rate_spin.setRange(0, 10000)
        ram_layout.addRow("Data Rate:", self.ram_data_rate_spin)

        self.ram_capacity_spin = QSpinBox()
        self.ram_capacity_spin.setRange(0, 1024)
        ram_layout.addRow("Capacity (GB):", self.ram_capacity_spin)

        self.ram_lighting_combo = QComboBox()
        self.ram_lighting_combo.setEditable(True)
        ram_layout.addRow("Lighting:", self.ram_lighting_combo)

        self.ram_tab.setLayout(ram_layout)
        tabs.addTab(self.ram_tab, "RAM")

        layout.addWidget(tabs)

        # --------------------- Buttons ---------------------
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # Populate the combo boxes using your backend
        self.populate_filter_options()

    def populate_filter_options(self):
        """
        Loads the component DataFrames, generates filter options, and populates
        the combo boxes accordingly. Blank entries indicate 'no filter'.
        """
        df_gpus, df_cpus, df_mbs, df_rams = load_specifications()
        df_gpus, df_cpus, df_mbs, df_rams = preprocess_data([df_gpus, df_cpus, df_mbs, df_rams])
        options = generate_all_filter_options(df_gpus, df_cpus, df_mbs, df_rams)

        # ------------------ GPU ------------------
        gpu_opts = options.get("GPUs", {})
        # Brand
        self.gpu_brand_combo.clear()
        self.gpu_brand_combo.addItem("")  # blank = no filter
        for val in gpu_opts.get("Brand", []):
            self.gpu_brand_combo.addItem(str(val))
        # Series
        self.gpu_series_combo.clear()
        self.gpu_series_combo.addItem("")
        for val in gpu_opts.get("Series", []):
            self.gpu_series_combo.addItem(str(val))
        # Manufacturer
        self.gpu_manufacturer_combo.clear()
        self.gpu_manufacturer_combo.addItem("")
        for val in gpu_opts.get("Manufacturer", []):
            self.gpu_manufacturer_combo.addItem(str(val))
        # PCIe Version
        self.gpu_pcie_version_combo.clear()
        self.gpu_pcie_version_combo.addItem("")
        for val in gpu_opts.get("PCIe Version", []):
            self.gpu_pcie_version_combo.addItem(str(val))
        # CUDA Ready
        self.gpu_cuda_ready_combo.clear()
        self.gpu_cuda_ready_combo.addItem("")  # blank means no filter
        for val in gpu_opts.get("CUDA Ready", []):
            # e.g., 0 or 1 or other possible categorical values
            self.gpu_cuda_ready_combo.addItem(str(val))

        # ------------------ CPU ------------------
        cpu_opts = options.get("CPUs", {})
        # Brand
        self.cpu_brand_combo.clear()
        self.cpu_brand_combo.addItem("")
        for val in cpu_opts.get("Brand", []):
            self.cpu_brand_combo.addItem(str(val))
        # Type
        self.cpu_type_combo.clear()
        self.cpu_type_combo.addItem("")
        for val in cpu_opts.get("Type", []):
            self.cpu_type_combo.addItem(str(val))
        # Series
        self.cpu_series_combo.clear()
        self.cpu_series_combo.addItem("")
        for val in cpu_opts.get("Series", []):
            self.cpu_series_combo.addItem(str(val))
        # CPU Socket
        self.cpu_socket_combo.clear()
        self.cpu_socket_combo.addItem("")
        for val in cpu_opts.get("CPU Socket", []):
            self.cpu_socket_combo.addItem(str(val))
        # Direct PCIe Version
        self.cpu_direct_pcie_combo.clear()
        self.cpu_direct_pcie_combo.addItem("")
        for val in cpu_opts.get("Direct PCIe Version", []):
            self.cpu_direct_pcie_combo.addItem(str(val))
        # Packaging
        self.cpu_packaging_combo.clear()
        self.cpu_packaging_combo.addItem("")
        for val in cpu_opts.get("Packaging", []):
            self.cpu_packaging_combo.addItem(str(val))
        # Cooler
        self.cpu_cooler_combo.clear()
        self.cpu_cooler_combo.addItem("")
        for val in cpu_opts.get("Cooler", []):
            self.cpu_cooler_combo.addItem(str(val))

        # ------------------ Motherboard ------------------
        mb_opts = options.get("MBs", {})
        # Manufacturer
        self.mb_manufacturer_combo.clear()
        self.mb_manufacturer_combo.addItem("")
        for val in mb_opts.get("Manufacturer", []):
            self.mb_manufacturer_combo.addItem(str(val))
        # Form Factor
        self.mb_form_factor_combo.clear()
        self.mb_form_factor_combo.addItem("")
        for val in mb_opts.get("Form Factor", []):
            self.mb_form_factor_combo.addItem(str(val))
        # CPU Socket
        self.mb_cpu_socket_combo.clear()
        self.mb_cpu_socket_combo.addItem("")
        for val in mb_opts.get("CPU Socket", []):
            self.mb_cpu_socket_combo.addItem(str(val))
        # Chipset
        self.mb_chipset_combo.clear()
        self.mb_chipset_combo.addItem("")
        for val in mb_opts.get("Chipset", []):
            self.mb_chipset_combo.addItem(str(val))
        # RAM Type
        self.mb_ram_type_combo.clear()
        self.mb_ram_type_combo.addItem("")
        for val in mb_opts.get("RAM Type", []):
            self.mb_ram_type_combo.addItem(str(val))
        # PCIe Version
        self.mb_pcie_version_combo.clear()
        self.mb_pcie_version_combo.addItem("")
        for val in mb_opts.get("PCIe Version", []):
            self.mb_pcie_version_combo.addItem(str(val))

        # ------------------ RAM ------------------
        ram_opts = options.get("RAMs", {})
        # Manufacturer
        self.ram_manufacturer_combo.clear()
        self.ram_manufacturer_combo.addItem("")
        for val in ram_opts.get("Manufacturer", []):
            self.ram_manufacturer_combo.addItem(str(val))
        # RAM Type
        self.ram_type_combo.clear()
        self.ram_type_combo.addItem("")
        for val in ram_opts.get("RAM Type", []):
            self.ram_type_combo.addItem(str(val))
        # Lighting
        self.ram_lighting_combo.clear()
        self.ram_lighting_combo.addItem("")
        for val in ram_opts.get("Lighting", []):
            self.ram_lighting_combo.addItem(str(val))

    def get_filters(self):
        """
        Retrieve filter settings for each component and return them as dictionaries.
        """
        # ------------------ GPU ------------------
        gpu_filters = {}
        if self.gpu_brand_combo.currentText():
            gpu_filters["Brand"] = self.gpu_brand_combo.currentText()
        if self.gpu_series_combo.currentText():
            gpu_filters["Series"] = [self.gpu_series_combo.currentText()]
        if self.gpu_manufacturer_combo.currentText():
            gpu_filters["Manufacturer"] = self.gpu_manufacturer_combo.currentText()
        if self.gpu_vram_min_edit.text():
            gpu_filters["Memory Capacity"] = (float(self.gpu_vram_min_edit.text()), None)
        if self.gpu_power_max_edit.text():
            gpu_filters["Power"] = (None, float(self.gpu_power_max_edit.text()))
        if self.gpu_cuda_ready_combo.currentText():
            # For a blank selection, you might want to ignore the filter:
            if self.gpu_cuda_ready_combo.currentText().strip() != "":
                gpu_filters["CUDA Ready"] = self.gpu_cuda_ready_combo.currentText()
        if self.gpu_pcie_version_combo.currentText():
            try:
                val = float(self.gpu_pcie_version_combo.currentText())
                gpu_filters["PCIe Version"] = val
            except ValueError:
                pass  # ignore non-numeric input

        # ------------------ CPU ------------------
        cpu_filters = {}
        if self.cpu_brand_combo.currentText():
            cpu_filters["Brand"] = self.cpu_brand_combo.currentText()
        if self.cpu_type_combo.currentText():
            cpu_filters["Type"] = self.cpu_type_combo.currentText()
        if self.cpu_series_combo.currentText():
            cpu_filters["Series"] = self.cpu_series_combo.currentText()
        cores = self.cpu_cores_min_spin.value()
        if cores:
            cpu_filters["Cores"] = (cores, None)
        threads = self.cpu_threads_min_spin.value()
        if threads:
            cpu_filters["Threads"] = (threads, None)
        if self.cpu_socket_combo.currentText():
            cpu_filters["CPU Socket"] = self.cpu_socket_combo.currentText()
        if self.cpu_direct_pcie_combo.currentText():
            try:
                val = float(self.cpu_direct_pcie_combo.currentText())
                cpu_filters["Direct PCIe Version"] = val
            except ValueError:
                pass
        if self.cpu_packaging_combo.currentText():
            cpu_filters["Packaging"] = [self.cpu_packaging_combo.currentText()]
        if self.cpu_cooler_combo.currentText():
            cpu_filters["Cooler"] = self.cpu_cooler_combo.currentText()

        # ------------------ Motherboard ------------------
        mb_filters = {}
        if self.mb_manufacturer_combo.currentText():
            mb_filters["Manufacturer"] = self.mb_manufacturer_combo.currentText()
        if self.mb_form_factor_combo.currentText():
            mb_filters["Form Factor"] = self.mb_form_factor_combo.currentText()
        if self.mb_cpu_socket_combo.currentText():
            mb_filters["CPU Socket"] = self.mb_cpu_socket_combo.currentText()
        if self.mb_chipset_combo.currentText():
            mb_filters["Chipset"] = [self.mb_chipset_combo.currentText()]
        if self.mb_ram_type_combo.currentText():
            mb_filters["RAM Type"] = self.mb_ram_type_combo.currentText()
        mb_capacity = self.mb_max_capacity_spin.value()
        if mb_capacity:
            mb_filters["Max Capacity"] = (mb_capacity, None)
        modules = self.mb_modules_spin.value()
        if modules:
            mb_filters["Modules"] = (modules, None)
        if self.mb_pcie_version_combo.currentText():
            try:
                val = float(self.mb_pcie_version_combo.currentText())
                mb_filters["PCIe Version"] = val
            except ValueError:
                pass

        # ------------------ RAM ------------------
        ram_filters = {}
        if self.ram_manufacturer_combo.currentText():
            ram_filters["Manufacturer"] = self.ram_manufacturer_combo.currentText()
        if self.ram_type_combo.currentText():
            ram_filters["RAM Type"] = self.ram_type_combo.currentText()
        data_rate = self.ram_data_rate_spin.value()
        if data_rate:
            ram_filters["Data Rate"] = (data_rate, None)
        capacity = self.ram_capacity_spin.value()
        if capacity:
            ram_filters["Capacity"] = (capacity, None)
        if self.ram_lighting_combo.currentText():
            ram_filters["Lighting"] = self.ram_lighting_combo.currentText()

        return gpu_filters, cpu_filters, mb_filters, ram_filters