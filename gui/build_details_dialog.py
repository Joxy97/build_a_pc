# gui/build_details_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel

class BuildDetailsDialog(QDialog):
    def __init__(self, build_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Build Details")
        
        layout = QVBoxLayout()
        
        # Example: show GPU, CPU, RAM, Price, etc.
        layout.addWidget(QLabel(f"GPU: {build_data['GPU']}"))
        layout.addWidget(QLabel(f"CPU: {build_data['CPU']}"))
        layout.addWidget(QLabel(f"RAM: {build_data['RAM']}"))
        layout.addWidget(QLabel(f"Total Price: {build_data['TotalPrice']}"))
        layout.addWidget(QLabel(f"Build Score: {build_data['BuildScore']}"))
        layout.addWidget(QLabel(f"Score-to-Price: {build_data['ScoreToPrice']}"))
        
        self.setLayout(layout)
