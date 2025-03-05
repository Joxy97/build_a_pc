from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About PC Builder")
        self.resize(400, 300)
        layout = QVBoxLayout(self)
        about_text = """
        <h2>PC Builder Prototype</h2>
        <p>This application helps you build a custom PC by selecting compatible components.</p>
        <p>Version 2.0 - Powered by PyQt6.</p>
        <p>More details will be added here.</p>
        """
        label = QLabel(about_text)
        label.setWordWrap(True)
        layout.addWidget(label)
        btn = QPushButton("Close")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)
