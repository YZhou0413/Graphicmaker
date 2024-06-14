from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QGridLayout, QFrame
from PyQt6.QtCore import Qt, pyqtSignal

class exporter(QWidget):
    bg_color_bool = pyqtSignal(bool)
    def __init__(self):
        super().__init__()
        self.setFixedSize(200, 200)
        layout = QVBoxLayout()
        self.frame = QFrame()
        self.button1 = QPushButton("with Background", self)
        self.button2 = QPushButton("no Background", self)
        self.b_bg_color = QPushButton("change color", self)
        self.b_bg_color.setCheckable(True)
        self.b_bg_color.clicked.connect(self.bg_color_signal)
        self.b_bg_pic = QPushButton("set a image", self)
        self.b_bg_pic.setCheckable(True)
    

        self.label0 = QLabel("edit background", self)
        self.label1 = QLabel("export as *.PNG", self)
        self.label1.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout = QGridLayout(self.frame)

        main_layout.addWidget(self.label0, 0, 0, 1, 2)
        main_layout.addWidget(self.b_bg_color, 1, 0, 1, 2)
        main_layout.addWidget(self.b_bg_pic, 2, 0, 1, 2)
        main_layout.addWidget(self.label1, 3, 0, 1, 2)
        main_layout.addWidget(self.button1, 4, 0, 1, 2)
        main_layout.addWidget(self.button2, 5, 0, 1, 2)
        layout.addWidget(self.frame)
        self.setLayout(layout)

    def bg_color_signal(self):
        if self.b_bg_color.isChecked():
            self.bg_color_bool.emit(True)
        else:
            self.bg_color_bool.emit(False)
        