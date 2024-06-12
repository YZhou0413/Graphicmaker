from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QGridLayout, QFrame
from PyQt6.QtCore import Qt

class exporter(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(300, 70)

        main_layout = QGridLayout()
        self.button1 = QPushButton("with Background", self)
        self.button2 = QPushButton("no Background", self)

        self.label = QLabel("export as *.PNG", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        main_layout.addWidget(self.label, 0, 1, 1, 2)
        main_layout.addWidget(self.button1, 1, 0, 1, 3)
        main_layout.addWidget(self.button2, 1, 4, 1, 3)
        self.setLayout(main_layout)
