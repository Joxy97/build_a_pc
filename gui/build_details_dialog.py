from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QScrollArea, QWidget
from PyQt6.QtCore import Qt

class BuildDetailsDialog(QDialog):
    def __init__(self, build_data: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Build Details")
        self.resize(600, 400)
        
        layout = QVBoxLayout(self)
        
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Display all detailed information from build_data.
        for key, value in build_data.items():
            label = QLabel(f"<b>{key}:</b> {value}")
            label.setWordWrap(True)
            content_layout.addWidget(label)
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        self.setLayout(layout)

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dummy_data = {
        "GPU": "NVIDIA GeForce RTX 3060",
        "CPU": "AMD Ryzen 9 9950X",
        "Motherboard": "ASRock A620M Pro RS",
        "RAM": "KF548C38BB-8",
        "Product": "Ryzen 9 9950X",
        "Code": "100-000001277",
        "Link": "http://example.com",
        "Packaging": "tray",
        "Cooler": "yes",
        "Other Specs": "Detailed specs go here."
    }
    dialog = BuildDetailsDialog(dummy_data)
    dialog.exec()
