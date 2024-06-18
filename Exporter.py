from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QGridLayout, QFrame
from PyQt6.QtCore import Qt, pyqtSignal

class exporter(QWidget):
    bg_color_bool = pyqtSignal(bool)
    save_bg_bool = pyqtSignal(bool)
    bg_pic = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setFixedSize(200, 220)
        layout = QVBoxLayout()
        self.frame = QFrame()
        self.button1 = QPushButton("with Background", self)
        self.button1.clicked.connect(self.save_bg_signal_true)
        self.button2 = QPushButton("no Background", self)
        self.button2.clicked.connect(self.save_bg_signal_false)
        self.b_bg_color = QPushButton("change color", self)
        self.b_bg_color.setCheckable(True)
        self.b_bg_color.clicked.connect(self.bg_color_signal)
        self.b_bg_pic = QPushButton("set a image", self)
        self.b_bg_pic.clicked.connect(self.b_pic_si)
        self.placeholder = QFrame(self)
        self.placeholder.setFixedHeight(5)
        self.placeholder.setFrameShape(QFrame.Shape.HLine)
        self.placeholder.setFrameShadow(QFrame.Shadow.Sunken)

    

        self.label0 = QLabel("edit background", self)
        self.label1 = QLabel("export as *.PNG", self)
        self.label1.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout = QGridLayout(self.frame)

        main_layout.addWidget(self.label0, 0, 0, 1, 2)
        main_layout.addWidget(self.b_bg_color, 1, 0, 1, 2)
        main_layout.addWidget(self.b_bg_pic, 2, 0, 1, 2)
        main_layout.addWidget(self.placeholder, 3, 0, 1, 2)
        main_layout.addWidget(self.label1, 4, 0, 1, 2)
        main_layout.addWidget(self.button1, 5, 0, 1, 2)
        main_layout.addWidget(self.button2, 6, 0, 1, 2)
        layout.addWidget(self.frame)
        self.setLayout(layout)

    def bg_color_signal(self):
        if self.b_bg_color.isChecked():
            self.bg_color_bool.emit(True)
        else:
            self.bg_color_bool.emit(False)
        
    def save_bg_signal_true(self):
        self.save_bg_bool.emit(True)

    def save_bg_signal_false(self):
        self.save_bg_bool.emit(False)

    def b_pic_si(self):
        self.bg_pic.emit()