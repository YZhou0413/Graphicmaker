import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QListWidget, QListWidgetItem, QAbstractItemView
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QCursor
from collections import OrderedDict
from PreviewWidget import PreviewGraphicsView
class MyListWidget(QListWidget):
    itemMoved = pyqtSignal(int, int)  # 自定义信号
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)
    def dropEvent(self, event):
        super().dropEvent(event)
        from_index = self.currentRow()
        to_index = self.row(self.itemAt(self.viewport().mapFromGlobal(QCursor.pos()))) if self.itemAt(self.viewport().mapFromGlobal(QCursor.pos())) else -1
        self.itemMoved.emit(from_index, to_index)

class LayerManager(QWidget):
    layers_change = pyqtSignal(dict)
    def __init__(self):
        super().__init__()
        self.layers = OrderedDict()
        self.selected_layer_index = -1
        self.init_ui()

    def init_ui(self):
        self.layer_list = MyListWidget()  
        self.layer_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)  
        self.layer_list.currentRowChanged.connect(self.set_layer_index)
        self.layer_list.itemMoved.connect(self.move_layer)  # 绑定自定义信号

        self.raise_button = QPushButton("Raise Layer")
        self.lower_button = QPushButton("Lower Layer")
        
        self.raise_button.clicked.connect(self.raise_layer)
        self.lower_button.clicked.connect(self.lower_layer)
        
        layout = QVBoxLayout()
        layout.addWidget(self.layer_list)
        layout.addWidget(self.raise_button)
        layout.addWidget(self.lower_button)
        self.setLayout(layout)
        self.preview = PreviewGraphicsView()

    def set_selected_styles(self, layers):
        self.layers = layers
        self.refresh_layers()
        self.update_layers()  # 添加这一行来确保在更新 self.layers 后立即更新 Preview

    def raise_layer(self):
        if self.selected_layer_index > 0:
            self.move_layer(self.selected_layer_index, self.selected_layer_index - 1)

    def lower_layer(self):
        if self.selected_layer_index < len(self.layers) - 1:
            self.move_layer(self.selected_layer_index, self.selected_layer_index + 1)


    def move_layer(self, from_index, to_index):
    # 获取被移动的键值对
        keys = list(self.layers.keys())
        values = list(self.layers.values())

        # 交换位置
        keys[from_index], keys[to_index] = keys[to_index], keys[from_index]
        values[from_index], values[to_index] = values[to_index], values[from_index]

        # 重建字典
        self.layers = OrderedDict(zip(keys, values))

        self.refresh_layers()
        self.layer_list.setCurrentRow(to_index)
        self.update_layers()

    def refresh_layers(self):
        self.layer_list.clear()
        for layer_name in self.layers.keys():
            self.layer_list.addItem(layer_name)

    def set_layer_index(self, index):
        self.selected_layer_index = index

    def update_layers(self):
        image_paths = list(self.layers.values())
        self.preview.update_preview(image_paths)
        self.show()



