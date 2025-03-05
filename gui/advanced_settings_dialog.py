from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

class AdvancedSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Advanced Settings")
        self.resize(400, 300)
        layout = QVBoxLayout(self)
        settings_text = """
        <h3>Advanced Settings</h3>
        <p>Here you can adjust additional parameters used by the recommendation system.</p>
        <p>(This is a placeholder. Actual settings will be implemented later.)</p>
        """
        label = QLabel(settings_text)
        label.setWordWrap(True)
        layout.addWidget(label)
        btn = QPushButton("Close")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)
