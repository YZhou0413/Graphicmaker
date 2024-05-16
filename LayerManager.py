import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QListWidget, QListWidgetItem, QAbstractItemView
from PyQt6.QtCore import pyqtSignal, QEvent
from PyQt6.QtGui import QCursor
from collections import OrderedDict, deque
from PreviewWidget import PreviewGraphicsView
class MyListWidget(QListWidget):
    itemMoved = pyqtSignal(int, int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)  

    def dropEvent(self, event: QEvent):
        super().dropEvent(event)
        from_index = self.currentRow()
        to_index = self.indexAt(event.position().toPoint()).row() if self.indexAt(event.position().toPoint()).isValid() else -1
        self.itemMoved.emit(from_index, to_index)



class LayerManager(QWidget):
    layers_change = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Layer Manager')
        self.layers = OrderedDict()
        self.selected_layer_index = -1
        self.preview = PreviewGraphicsView()
        self.init_ui()

    def init_ui(self):
        self.layer_list = MyListWidget()    
        self.layer_list.currentRowChanged.connect(self.set_layer_index)
        self.layer_list.itemMoved.connect(self.handle_item_moved)  

        self.lower_button = QPushButton("Lower Layer")
        self.raise_button = QPushButton("Raise Layer")
        
        self.lower_button.clicked.connect(lambda: self.lower_layer(self.selected_layer_index))
        self.raise_button.clicked.connect(lambda: self.raise_layer(self.selected_layer_index))
        
        layout = QVBoxLayout()
        layout.addWidget(self.layer_list)
        layout.addWidget(self.lower_button)
        layout.addWidget(self.raise_button)
        self.setLayout(layout)

    def set_selected_styles(self, layers):
        self.layers = layers
        self.refresh_layers()
        self.update_layers() 

    def move_item_in_list(self, from_index, to_index):
        if from_index == to_index or from_index < 0 or to_index < 0 or from_index >= self.layer_list.count() or to_index >= self.layer_list.count():
            return

        # 在列表中移动项
        item = self.layer_list.takeItem(from_index)
        self.layer_list.insertItem(to_index, item)
        self.layer_list.setCurrentRow(to_index)

        # 触发字典移动函数
        self.move_item_in_dict(from_index, to_index)
        self.refresh_layers()
        self.update_layers()

    # 字典移动函数
    def move_item_in_dict(self, from_index, to_index):
        keys = list(self.layers.keys())
        values = list(self.layers.values())
        if to_index < 0 or to_index >= len(keys):
            return
        # 在字典中进行索引转换
        dict_from_index = len(keys) - 1 - from_index
        dict_to_index = len(keys) - 1 - to_index

        # 交换键和值
        keys[dict_from_index], keys[dict_to_index] = keys[dict_to_index], keys[dict_from_index]
        values[dict_from_index], values[dict_to_index] = values[dict_to_index], values[dict_from_index]

        # 更新字典
        self.layers = OrderedDict(zip(keys, values))

        # 刷新图层预览
        self.refresh_layers()
        self.update_layers()

    # Lower按钮点击事件处理函数
    def lower_layer(self, selected_layer_index):
        to_index = selected_layer_index + 1  # 更新选中图层的索引
        self.move_item_in_dict(selected_layer_index, to_index)
        self.layer_list.setCurrentRow(to_index)


    # Raise按钮点击事件处理函数
    def raise_layer(self, selected_layer_index):
        to_index = selected_layer_index - 1  # 更新选中图层的索引
        self.move_item_in_dict(selected_layer_index, to_index)
        self.layer_list.setCurrentRow(to_index)


    # 列表项移动事件处理函数
    def handle_item_moved(self, from_index, to_index):
        self.move_item_in_list(from_index, to_index)

    def refresh_layers(self):
        self.layer_list.clear()
        for layer_name in reversed(list(self.layers.keys())):  # 从右到左遍历字典
            self.layer_list.addItem(layer_name)

    def set_layer_index(self, index):
        self.selected_layer_index = index

    def update_layers(self):
        image_paths = list(self.layers.values())
        self.preview.update_preview(image_paths)
        self.show()



