import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QListWidget, QListWidgetItem
from PyQt6.QtCore import pyqtSignal
class LayerManager(QMainWindow):
    layers_change = pyqtSignal(list)
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Layer Manager")
        self.setGeometry(100, 100, 300, 400)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.layer_list = QListWidget()
        self.layout.addWidget(self.layer_list)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_layers)
        self.layout.addWidget(self.refresh_button)

        self.raise_button = QPushButton("Raise Layer")
        self.raise_button.clicked.connect(self.raise_layer)
        self.layout.addWidget(self.raise_button)

        self.lower_button = QPushButton("Lower Layer")
        self.lower_button.clicked.connect(self.lower_layer)
        self.layout.addWidget(self.lower_button)

        self.layers = []  # 存储图层信息，每个图层包含图层名和图像路径
        self.selected_layer_index = None 


    def set_selected_styles(self, selected_styles):
        self.layers = []  # 清空现有的图层信息
        for style in selected_styles:
            self.layers.append({"name": style})
        self.refresh_layers()


    def raise_layer(self, selected_style):
        for i, layer in enumerate(self.layers):
            if layer["name"] == selected_style:
                if i > 0:
                    self.layers[i], self.layers[i - 1] = self.layers[i - 1], self.layers[i]
                    self.refresh_layers()
                    self.layer_list.setCurrentRow(i - 1)
                    break 
        self.layers_change.emit(self.layers)

    def lower_layer(self, selected_style):
        for i, layer in enumerate(self.layers):
            if layer["name"] == selected_style:
                if i < len(self.layers) - 1:
                    self.layers[i], self.layers[i + 1] = self.layers[i + 1], self.layers[i]
                    self.refresh_layers()
                    self.layer_list.setCurrentRow(i + 1)
                    break
        self.layers_change.emit(self.layers)

    def refresh_layers(self):
        self.layer_list.clear()
        for layer_info in self.layers:
            self.layer_list.addItem(layer_info["name"])

    def set_layer_index(self, index):
        self.selected_layer_index = index
    
    def update_layers(self):
        self.refresh_layers()
        self.show()

